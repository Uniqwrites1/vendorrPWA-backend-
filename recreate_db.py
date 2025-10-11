"""
Simple script to recreate the database with correct schema
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.models import Base, User, UserRole
from passlib.context import CryptContext

# Create SQLite database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def recreate_database():
    """Recreate database with correct schema"""
    print("Creating database tables...")

    # Drop all tables and recreate
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("Adding basic admin user...")
    db = SessionLocal()

    try:
        # Create admin user
        admin_user = User(
            email="admin@vendorr.com",
            phone="+1234567890",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)

        # Create test customer
        test_customer = User(
            email="customer@test.com",
            phone="+1234567893",
            hashed_password=get_password_hash("test123"),
            first_name="Test",
            last_name="Customer",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        db.add(test_customer)

        db.commit()
        print("Database recreated successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    recreate_database()
