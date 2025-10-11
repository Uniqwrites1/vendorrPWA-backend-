"""
OAuth authentication services for Google and Facebook
"""
import httpx
from typing import Optional, Dict
from fastapi import HTTPException, status
import logging
import os

logger = logging.getLogger(__name__)

# OAuth configuration - these should be set in environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")


class OAuth Provider:
    """Base OAuth provider class"""

    async def verify_token(self, token: str) -> Dict:
        """Verify OAuth token and return user info"""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider"""

    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"
    GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"

    async def verify_token(self, access_token: str) -> Dict:
        """
        Verify Google OAuth access token and return user info

        Args:
            access_token: Google OAuth access token

        Returns:
            Dict with user info: {
                "id": str,
                "email": str,
                "name": str,
                "picture": str,
                "email_verified": bool
            }
        """
        try:
            async with httpx.AsyncClient() as client:
                # First, verify the token
                token_response = await client.get(
                    self.GOOGLE_TOKEN_INFO_URL,
                    params={"access_token": access_token}
                )

                if token_response.status_code != 200:
                    logger.error(f"Google token verification failed: {token_response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Google token"
                    )

                token_data = token_response.json()

                # Verify the token is for our application
                if GOOGLE_CLIENT_ID and token_data.get("aud") != GOOGLE_CLIENT_ID:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token not issued for this application"
                    )

                # Get user info
                user_response = await client.get(
                    self.GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                if user_response.status_code != 200:
                    logger.error(f"Failed to get Google user info: {user_response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Failed to get user information"
                    )

                user_data = user_response.json()

                return {
                    "id": user_data.get("sub"),
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "picture": user_data.get("picture"),
                    "email_verified": user_data.get("email_verified", False)
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying Google token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify Google authentication"
            )


class FacebookOAuthProvider(OAuthProvider):
    """Facebook OAuth provider"""

    FACEBOOK_GRAPH_URL = "https://graph.facebook.com/v18.0"

    async def verify_token(self, access_token: str) -> Dict:
        """
        Verify Facebook OAuth access token and return user info

        Args:
            access_token: Facebook OAuth access token

        Returns:
            Dict with user info: {
                "id": str,
                "email": str,
                "name": str,
                "picture": str
            }
        """
        try:
            async with httpx.AsyncClient() as client:
                # Verify token and get user data
                response = await client.get(
                    f"{self.FACEBOOK_GRAPH_URL}/me",
                    params={
                        "access_token": access_token,
                        "fields": "id,name,email,picture.type(large)"
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Facebook token verification failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Facebook token"
                    )

                user_data = response.json()

                # Verify we got required fields
                if not user_data.get("id"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid Facebook user data"
                    )

                return {
                    "id": user_data.get("id"),
                    "email": user_data.get("email"),  # May be None if not granted
                    "name": user_data.get("name"),
                    "picture": user_data.get("picture", {}).get("data", {}).get("url")
                }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying Facebook token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify Facebook authentication"
            )


# Provider instances
google_provider = GoogleOAuthProvider()
facebook_provider = FacebookOAuthProvider()


async def verify_oauth_token(provider: str, token: str) -> Dict:
    """
    Verify OAuth token for the specified provider

    Args:
        provider: OAuth provider name ("google" or "facebook")
        token: OAuth access token

    Returns:
        Dict with user information

    Raises:
        HTTPException: If verification fails
    """
    if provider == "google":
        return await google_provider.verify_token(token)
    elif provider == "facebook":
        return await facebook_provider.verify_token(token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )


def is_oauth_configured(provider: str) -> bool:
    """Check if OAuth provider is configured"""
    if provider == "google":
        return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    elif provider == "facebook":
        return bool(FACEBOOK_APP_ID and FACEBOOK_APP_SECRET)
    return False
