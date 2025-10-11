"""
Simple database initialization script
"""
import os
import sys

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.models import Base

# Create SQLite database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def init_db():
    """Initialize database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    init_db()
