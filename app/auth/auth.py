from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from ..core.config import settings
from ..core.database import get_db
from ..models.database_models import User, UserRole
from ..schemas import TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()

class AuthService:
    """Authentication service for handling JWT tokens and password hashing"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token_data = TokenData(user_id=user_id, email=email)
            return token_data

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Standalone helper functions for convenience
def decode_access_token(token: str) -> dict:
    """Decode JWT token and return payload"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authentication dependencies
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = AuthService.verify_token(token)

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    return current_user

# Role-based access control
class RoleChecker:
    """Role-based access control decorator"""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return current_user

# Pre-defined role checkers
require_admin = RoleChecker([UserRole.ADMIN])
require_manager = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
require_staff = RoleChecker([
    UserRole.ADMIN,
    UserRole.MANAGER,
    UserRole.KITCHEN_STAFF,
    UserRole.COUNTER_STAFF
])
require_customer = RoleChecker([UserRole.CUSTOMER])

# User service functions
def authenticate_user(email: str, password: str, db: Session) -> Union[User, bool]:
    """Authenticate user with email and password"""
    import logging
    logger = logging.getLogger(__name__)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        logger.debug(f"User not found: {email}")
        return False

    if not user.hashed_password:
        logger.error(f"User {email} has no hashed_password!")
        return False

    if not AuthService.verify_password(password, user.hashed_password):
        logger.debug(f"Password verification failed for: {email}")
        return False

    logger.info(f"Authentication successful for: {email}")
    return user

def get_user_by_email(email: str, db: Session) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(phone: str, db: Session) -> Optional[User]:
    """Get user by phone number"""
    return db.query(User).filter(User.phone == phone).first()

def create_user(user_data: dict, db: Session) -> User:
    """Create a new user"""
    # Hash password
    if user_data.get("password"):
        user_data["hashed_password"] = AuthService.get_password_hash(user_data.pop("password"))

    # Create user
    user = User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_login_time(user: User, db: Session):
    """Update user's last login time"""
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

# OAuth helper functions (placeholder for Google/Facebook integration)
def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token and return user info"""
    # TODO: Implement Google OAuth verification
    # This would use google.oauth2.id_token.verify_oauth2_token
    raise NotImplementedError("Google OAuth not implemented yet")

def verify_facebook_token(token: str) -> dict:
    """Verify Facebook OAuth token and return user info"""
    # TODO: Implement Facebook OAuth verification
    # This would use Facebook Graph API
    raise NotImplementedError("Facebook OAuth not implemented yet")

def get_or_create_oauth_user(provider: str, oauth_data: dict, db: Session) -> User:
    """Get or create user from OAuth data"""
    if provider == "google":
        user = db.query(User).filter(User.google_id == oauth_data["id"]).first()
        if not user:
            # Create new user from Google data
            user_data = {
                "email": oauth_data["email"],
                "first_name": oauth_data["given_name"],
                "last_name": oauth_data["family_name"],
                "google_id": oauth_data["id"],
                "is_verified": True,  # OAuth users are pre-verified
            }
            user = create_user(user_data, db)

    elif provider == "facebook":
        user = db.query(User).filter(User.facebook_id == oauth_data["id"]).first()
        if not user:
            # Create new user from Facebook data
            name_parts = oauth_data["name"].split(" ", 1)
            user_data = {
                "email": oauth_data.get("email"),
                "first_name": name_parts[0],
                "last_name": name_parts[1] if len(name_parts) > 1 else "",
                "facebook_id": oauth_data["id"],
                "is_verified": True,  # OAuth users are pre-verified
            }
            user = create_user(user_data, db)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported OAuth provider"
        )

    return user
