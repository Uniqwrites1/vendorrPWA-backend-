from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import logging

from ..core.database import get_db
from ..core.config import settings
from ..auth.auth import (
    AuthService, authenticate_user, get_user_by_email, get_user_by_phone,
    create_user, update_user_login_time, get_current_user, get_current_active_user
)
from ..schemas import (
    UserCreate, UserResponse, UserLogin, Token, OAuthRequest,
    APIResponse, ErrorResponse
)
from ..models.database_models import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=APIResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        if user_data.email and get_user_by_email(user_data.email, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        if user_data.phone and get_user_by_phone(user_data.phone, db):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )

        # Create user
        user_dict = user_data.model_dump(exclude={"confirm_password"})
        user = create_user(user_dict, db)

        return APIResponse(
            message="User registered successfully",
            data={"user_id": str(user.id)}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user with email and password"""
    try:
        # Debug: Log the incoming credentials (without password)
        print(f"DEBUG: Login attempt for email: {user_credentials.email}")

        # Authenticate user
        user = authenticate_user(user_credentials.email, user_credentials.password, db)
        if not user:
            print(f"DEBUG: Authentication failed for email: {user_credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login time
        update_user_login_time(user, db)

        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error for {user_credentials.email}: {str(e)}")
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/oauth", response_model=Token)
async def oauth_login(oauth_data: OAuthRequest, db: Session = Depends(get_db)):
    """Login with OAuth provider (Google/Facebook)"""
    from ..services.oauth_service import verify_oauth_token

    try:
        # Verify OAuth token and get user info
        oauth_user_info = await verify_oauth_token(oauth_data.provider, oauth_data.token)

        # Check if user exists by OAuth ID
        provider_id_field = f"{oauth_data.provider}_id"
        user = None

        if oauth_data.provider == "google":
            user = db.query(User).filter(User.google_id == oauth_user_info["id"]).first()
        elif oauth_data.provider == "facebook":
            user = db.query(User).filter(User.facebook_id == oauth_user_info["id"]).first()

        # If not found by OAuth ID, try to find by email
        if not user and oauth_user_info.get("email"):
            user = db.query(User).filter(User.email == oauth_user_info["email"]).first()

            # Link OAuth ID to existing account
            if user:
                if oauth_data.provider == "google":
                    user.google_id = oauth_user_info["id"]
                elif oauth_data.provider == "facebook":
                    user.facebook_id = oauth_user_info["id"]
                db.commit()

        # Create new user if doesn't exist
        if not user:
            # Split name into first and last name
            full_name = oauth_user_info.get("name", "")
            name_parts = full_name.split(" ", 1) if full_name else ["User", ""]
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""

            user = User(
                email=oauth_user_info.get("email"),
                first_name=first_name,
                last_name=last_name,
                hashed_password=None,  # No password for OAuth users
                role="customer",
                is_active=True,
                is_verified=True,  # OAuth users are pre-verified
                google_id=oauth_user_info["id"] if oauth_data.provider == "google" else None,
                facebook_id=oauth_user_info["id"] if oauth_data.provider == "facebook" else None
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )

        # Create access token
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Update user fields
        for field, value in user_update.items():
            if hasattr(current_user, field) and field not in ["id", "created_at", "updated_at"]:
                setattr(current_user, field, value)

        db.commit()
        db.refresh(current_user)

        return UserResponse.model_validate(current_user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )

@router.post("/change-password", response_model=APIResponse)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not AuthService.verify_password(current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        current_user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()

        return APIResponse(message="Password changed successfully")

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.post("/logout", response_model=APIResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client-side token removal)"""
    # Note: With JWT, logout is primarily handled client-side
    # In a production app, you might want to implement token blacklisting
    return APIResponse(message="Logged out successfully")

@router.post("/refresh-token", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)):
    """Refresh access token"""
    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = AuthService.create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email},
            expires_delta=access_token_expires
        )

        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=UserResponse.model_validate(current_user)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

@router.post("/verify-token", response_model=APIResponse)
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify if current token is valid"""
    return APIResponse(
        message="Token is valid",
        data={
            "user_id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role
        }
    )
