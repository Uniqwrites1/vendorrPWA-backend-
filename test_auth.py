"""
Test authentication system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models import User
from app.auth.auth import authenticate_user
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_auth():
    db = next(get_db())

    print("=== Testing Authentication ===")

    # Get test users
    users = db.query(User).all()
    print(f"Found {len(users)} users:")

    for user in users:
        print(f"  - ID: {user.id}, Email: {user.email}, Role: {user.role}")

        # Test password verification for customer
        if user.email == "customer@test.com":
            print(f"    Testing password for {user.email}:")
            print(f"    Stored hash: {user.hashed_password[:50]}...")

            # Test direct password verification
            is_valid = pwd_context.verify("test123", user.hashed_password)
            print(f"    Direct bcrypt verify: {is_valid}")

            # Test through auth service
            auth_user = authenticate_user("customer@test.com", "test123", db)
            print(f"    Auth service result: {auth_user is not None}")

    db.close()

if __name__ == "__main__":
    test_auth()
