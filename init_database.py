"""
Initialize the database with tables and seed data
"""
import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.core.init_db import create_tables, seed_database

if __name__ == "__main__":
    print("Creating database tables...")
    create_tables()
    print("Seeding database with initial data...")
    seed_database()
    print("Database initialization complete!")
