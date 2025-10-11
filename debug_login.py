"""
Debug login issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.auth.auth import authenticate_user, AuthService
from app.models import User

def debug_login():
    db = next(get_db())

    print("=== Debug Login Process ===")

    # Test user lookup
    email = "customer@test.com"
    user = db.query(User).filter(User.email == email).first()
    print(f"User found: {user is not None}")

    if user:
        print(f"User ID: {user.id}")
        print(f"User email: {user.email}")
        print(f"User has hashed_password: {hasattr(user, 'hashed_password')}")
        if hasattr(user, 'hashed_password'):
            print(f"Password hash: {user.hashed_password[:20]}...")

        # Test password verification
        test_password = "test123"
        try:
            is_valid = AuthService.verify_password(test_password, user.hashed_password)
            print(f"Password verification result: {is_valid}")
        except Exception as e:
            print(f"Password verification error: {e}")

        # Test authenticate_user function
        try:
            auth_result = authenticate_user(email, test_password, db)
            print(f"authenticate_user result: {auth_result}")
            print(f"Result type: {type(auth_result)}")
        except Exception as e:
            print(f"authenticate_user error: {e}")

        # Test JWT token creation
        try:
            from datetime import timedelta
            from app.core.config import settings
            token = AuthService.create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=timedelta(minutes=30)
            )
            print(f"Token creation successful: {token[:20]}...")
        except Exception as e:
            print(f"Token creation error: {e}")

    db.close()

if __name__ == "__main__":
    debug_login()
