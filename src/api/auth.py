# src/api/auth.py - Authentication with PostgreSQL

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging
import json

from config.settings import settings
from config.constants import AUTH
from database.db_pool import get_db_connection

logger = logging.getLogger(__name__)

# Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# JWT settings
ALGORITHM = AUTH["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = AUTH["ACCESS_TOKEN_EXPIRE_MINUTES"]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

class UserInDB(User):
    password_hash: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

def verify_password(plain_password, hashed_password):
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Generate password hash."""
    return pwd_context.hash(password)

def get_user_by_username(username: str) -> Optional[UserInDB]:
    """Get user from database by username."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, password_hash, is_active, is_admin
                FROM users
                WHERE username = %s AND is_active = true
            """, (username,))
            
            row = cursor.fetchone()
            if row:
                return UserInDB(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    password_hash=row[4],
                    is_active=row[5],
                    is_admin=row[6]
                )
    return None

def get_user_by_id(user_id: int) -> Optional[UserInDB]:
    """Get user from database by ID."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, password_hash, is_active, is_admin
                FROM users
                WHERE id = %s AND is_active = true
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return UserInDB(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    full_name=row[3],
                    password_hash=row[4],
                    is_active=row[5],
                    is_admin=row[6]
                )
    return None

def create_user(user_data: UserCreate) -> Optional[User]:
    """Create a new user in the database."""
    password_hash = get_password_hash(user_data.password)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, full_name, password_hash)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, username, email, full_name, is_active, is_admin
                """, (user_data.username, user_data.email, user_data.full_name, password_hash))
                
                row = cursor.fetchone()
                conn.commit()
                
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        is_active=row[4],
                        is_admin=row[5]
                    )
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user."""
    user = get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (user.id,))
                conn.commit()
    except Exception as e:
        logger.warning(f"Failed to update last login: {e}")
    
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin
    )

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin privileges."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def log_user_action(user_id: int, action: str, details: Dict[str, Any] = None, 
                   ip_address: str = None, user_agent: str = None):
    """Log user actions for audit trail."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_audit_log (user_id, action, details, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, action, json.dumps(details) if details else None, 
                     ip_address, user_agent))
                conn.commit()
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")