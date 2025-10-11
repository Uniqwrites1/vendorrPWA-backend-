"""
Debug customer login issue
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def debug_customer():
    db = next(get_db())

    print("=== Customer Account Debug ===")

    # Get customer user
    customer = db.query(User).filter(User.email == "customer@test.com").first()

    if customer:
        print(f"Customer found:")
        print(f"  ID: {customer.id}")
        print(f"  Email: {customer.email}")
        print(f"  Role: {customer.role}")
        print(f"  Active: {customer.is_active}")
        print(f"  Verified: {customer.is_verified}")
        print(f"  Password hash: {customer.hashed_password[:50]}...")

        # Test password verification
        test_password = "test123"
        is_valid = pwd_context.verify(test_password, customer.hashed_password)
        print(f"  Password 'test123' valid: {is_valid}")

    else:
        print("Customer not found!")

    # List all users
    print("\n=== All Users ===")
    users = db.query(User).all()
    for user in users:
        print(f"  {user.email} - {user.role} - Active: {user.is_active}")

    db.close()

if __name__ == "__main__":
    debug_customer()
