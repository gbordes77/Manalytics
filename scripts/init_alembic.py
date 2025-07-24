#!/usr/bin/env python3
# scripts/init_alembic.py - Initialize Alembic

import subprocess
import os
from pathlib import Path

def init_alembic():
    """Initialize Alembic for database migrations."""
    
    # Check if alembic is installed
    try:
        import alembic
    except ImportError:
        print("Installing alembic...")
        subprocess.run(["pip", "install", "alembic==1.13.0"])
    
    # Initialize alembic if not already done
    if not Path("alembic.ini").exists():
        print("Initializing alembic...")
        subprocess.run(["alembic", "init", "migrations"])
        print("✅ Alembic initialized. Please update alembic.ini with your database URL.")
    else:
        print("Alembic already initialized.")
    
    # Run migrations
    print("Running migrations...")
    subprocess.run(["alembic", "upgrade", "head"])
    print("✅ Migrations complete!")

if __name__ == "__main__":
    init_alembic()