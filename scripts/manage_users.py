#!/usr/bin/env python3
"""
User management script for Manalytics.
Create, update, and manage users from the command line.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
import getpass
from tabulate import tabulate
from datetime import datetime

from database.db_pool import get_db_connection
from src.api.auth import get_password_hash, verify_password, get_user_by_username

@click.group()
def cli():
    """Manalytics user management tool."""
    pass

@cli.command()
@click.option('--username', prompt=True, help='Username (alphanumeric and underscore only)')
@click.option('--email', prompt=True, help='Email address')
@click.option('--full-name', prompt='Full name', help='Full name (optional)', default='')
@click.option('--admin', is_flag=True, help='Give admin privileges')
@click.option('--password', help='Password (will prompt if not provided)')
def create(username, email, full_name, admin, password):
    """Create a new user."""
    # Validate username
    if not username.replace('_', '').isalnum():
        click.echo("❌ Username must be alphanumeric (underscores allowed)")
        return
    
    # Check if user exists
    existing = get_user_by_username(username)
    if existing:
        click.echo(f"❌ User '{username}' already exists")
        return
    
    # Get password
    if not password:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            click.echo("❌ Passwords don't match")
            return
    
    if len(password) < 8:
        click.echo("❌ Password must be at least 8 characters")
        return
    
    # Create user
    password_hash = get_password_hash(password)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, full_name, password_hash, is_admin)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (username, email, full_name or None, password_hash, admin))
                
                user_id = cursor.fetchone()[0]
                conn.commit()
                
                click.echo(f"✅ User '{username}' created successfully (ID: {user_id})")
                if admin:
                    click.echo("   🔑 Admin privileges granted")
                    
    except Exception as e:
        click.echo(f"❌ Error creating user: {e}")

@cli.command()
def list():
    """List all users."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, full_name, is_active, is_admin, 
                           created_at, last_login
                    FROM users
                    ORDER BY created_at DESC
                """)
                
                rows = cursor.fetchall()
                
                if not rows:
                    click.echo("No users found")
                    return
                
                # Format data for display
                headers = ["ID", "Username", "Email", "Full Name", "Active", "Admin", "Created", "Last Login"]
                table_data = []
                
                for row in rows:
                    table_data.append([
                        row[0],
                        row[1],
                        row[2],
                        row[3] or "",
                        "✅" if row[4] else "❌",
                        "👑" if row[5] else "",
                        row[6].strftime("%Y-%m-%d") if row[6] else "",
                        row[7].strftime("%Y-%m-%d %H:%M") if row[7] else "Never"
                    ])
                
                click.echo("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
                click.echo(f"\nTotal users: {len(rows)}")
                
    except Exception as e:
        click.echo(f"❌ Error listing users: {e}")

@cli.command()
@click.argument('username')
@click.option('--password', help='New password (will prompt if not provided)')
def reset_password(username, password):
    """Reset a user's password."""
    # Check user exists
    user = get_user_by_username(username)
    if not user:
        click.echo(f"❌ User '{username}' not found")
        return
    
    # Get new password
    if not password:
        password = getpass.getpass("New password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            click.echo("❌ Passwords don't match")
            return
    
    if len(password) < 8:
        click.echo("❌ Password must be at least 8 characters")
        return
    
    # Update password
    password_hash = get_password_hash(password)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                """, (password_hash, username))
                conn.commit()
                
                click.echo(f"✅ Password reset for user '{username}'")
                
    except Exception as e:
        click.echo(f"❌ Error resetting password: {e}")

@cli.command()
@click.argument('username')
def make_admin(username):
    """Grant admin privileges to a user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET is_admin = true, updated_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                    RETURNING id
                """, (username,))
                
                result = cursor.fetchone()
                if result:
                    conn.commit()
                    click.echo(f"✅ User '{username}' is now an admin")
                else:
                    click.echo(f"❌ User '{username}' not found")
                    
    except Exception as e:
        click.echo(f"❌ Error updating user: {e}")

@cli.command()
@click.argument('username')
def revoke_admin(username):
    """Revoke admin privileges from a user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET is_admin = false, updated_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                    RETURNING id
                """, (username,))
                
                result = cursor.fetchone()
                if result:
                    conn.commit()
                    click.echo(f"✅ Admin privileges revoked for '{username}'")
                else:
                    click.echo(f"❌ User '{username}' not found")
                    
    except Exception as e:
        click.echo(f"❌ Error updating user: {e}")

@cli.command()
@click.argument('username')
def deactivate(username):
    """Deactivate a user account."""
    if username == 'admin':
        click.echo("❌ Cannot deactivate the admin account")
        return
        
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET is_active = false, updated_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                    RETURNING id
                """, (username,))
                
                result = cursor.fetchone()
                if result:
                    conn.commit()
                    click.echo(f"✅ User '{username}' deactivated")
                else:
                    click.echo(f"❌ User '{username}' not found")
                    
    except Exception as e:
        click.echo(f"❌ Error deactivating user: {e}")

@cli.command()
@click.argument('username')
def activate(username):
    """Reactivate a user account."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET is_active = true, updated_at = CURRENT_TIMESTAMP
                    WHERE username = %s
                    RETURNING id
                """, (username,))
                
                result = cursor.fetchone()
                if result:
                    conn.commit()
                    click.echo(f"✅ User '{username}' activated")
                else:
                    click.echo(f"❌ User '{username}' not found")
                    
    except Exception as e:
        click.echo(f"❌ Error activating user: {e}")

@cli.command()
@click.argument('username')
def info(username):
    """Show detailed information about a user."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Get user info
                cursor.execute("""
                    SELECT id, username, email, full_name, is_active, is_admin,
                           created_at, updated_at, last_login
                    FROM users
                    WHERE username = %s
                """, (username,))
                
                user = cursor.fetchone()
                if not user:
                    click.echo(f"❌ User '{username}' not found")
                    return
                
                # Get recent activity
                cursor.execute("""
                    SELECT action, created_at, ip_address
                    FROM user_audit_log
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (user[0],))
                
                activities = cursor.fetchall()
                
                # Display user info
                click.echo("\n" + "=" * 60)
                click.echo(f"User Information: {username}")
                click.echo("=" * 60)
                click.echo(f"ID:          {user[0]}")
                click.echo(f"Email:       {user[2]}")
                click.echo(f"Full Name:   {user[3] or 'Not set'}")
                click.echo(f"Status:      {'Active' if user[4] else 'Inactive'}")
                click.echo(f"Admin:       {'Yes' if user[5] else 'No'}")
                click.echo(f"Created:     {user[6]}")
                click.echo(f"Updated:     {user[7]}")
                click.echo(f"Last Login:  {user[8] or 'Never'}")
                
                if activities:
                    click.echo("\nRecent Activity:")
                    click.echo("-" * 60)
                    for activity in activities:
                        click.echo(f"  {activity[1].strftime('%Y-%m-%d %H:%M')} - {activity[0]} (IP: {activity[2] or 'N/A'})")
                        
    except Exception as e:
        click.echo(f"❌ Error getting user info: {e}")

@cli.command()
def create_default_admin():
    """Create the default admin user (if it doesn't exist)."""
    username = "admin"
    
    # Check if admin exists
    existing = get_user_by_username(username)
    if existing:
        click.echo(f"ℹ️  Admin user already exists")
        return
    
    # Create admin with default password
    password = "changeme"
    password_hash = get_password_hash(password)
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, full_name, password_hash, is_admin)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (username, "admin@manalytics.com", "Administrator", password_hash, True))
                
                user_id = cursor.fetchone()[0]
                conn.commit()
                
                click.echo(f"✅ Default admin user created")
                click.echo(f"   Username: admin")
                click.echo(f"   Password: changeme")
                click.echo(f"   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
                
    except Exception as e:
        click.echo(f"❌ Error creating admin: {e}")

if __name__ == "__main__":
    # Add tabulate to requirements if not present
    try:
        import tabulate
    except ImportError:
        click.echo("Installing required package: tabulate")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        
    cli()