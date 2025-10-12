from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import Optional
from app.core.database import get_db
from app.models.database_models import User, UserRole, AppSettings
from app.auth.auth import AuthService

router = APIRouter(prefix="/api/settings", tags=["settings"])

class WhatsAppSettings(BaseModel):
    whatsapp_link: str

class WhatsAppResponse(BaseModel):
    whatsapp_link: str
    whatsapp_enabled: bool
    restaurant_name: Optional[str] = None
    restaurant_phone: Optional[str] = None
    restaurant_email: Optional[str] = None
    restaurant_address: Optional[str] = None

@router.get("/whatsapp", response_model=WhatsAppResponse)
async def get_whatsapp_link(db: Session = Depends(get_db)):
    """Get the WhatsApp link and restaurant settings for customer support"""
    settings = db.query(AppSettings).first()

    if settings:
        return WhatsAppResponse(
            whatsapp_link=settings.whatsapp_link or "https://wa.me/qr/EKAYKJ7XOVOTP1",
            whatsapp_enabled=settings.whatsapp_enabled,
            restaurant_name=settings.restaurant_name,
            restaurant_phone=settings.restaurant_phone,
            restaurant_email=settings.restaurant_email,
            restaurant_address=settings.restaurant_address
        )

    # Fallback to default if no settings found
    return WhatsAppResponse(
        whatsapp_link="https://wa.me/qr/EKAYKJ7XOVOTP1",
        whatsapp_enabled=True,
        restaurant_name="Vendorr",
        restaurant_phone="+234 906 455 4795",
        restaurant_email="vendorr1@gmail.com",
        restaurant_address="Red Brick, Faculty of Arts, University of Jos"
    )

@router.put("/whatsapp")
async def update_whatsapp_link(
    settings: WhatsAppSettings,
    db: Session = Depends(get_db)
):
    """Update WhatsApp link (Admin only)

    Note: This endpoint is kept for future API-based updates.
    Currently, updates are done through the admin dashboard at /admin/settings
    """
    # TODO: Add admin authentication check here
    # Example:
    # user = await get_current_admin_user(...)
    # if user.role != UserRole.ADMIN:
    #     raise HTTPException(status_code=403, detail="Admin access required")

    app_settings = db.query(AppSettings).first()

    if not app_settings:
        # Create settings if they don't exist
        app_settings = AppSettings(whatsapp_link=settings.whatsapp_link)
        db.add(app_settings)
    else:
        app_settings.whatsapp_link = settings.whatsapp_link

    db.commit()
    db.refresh(app_settings)

    return {
        "message": "WhatsApp link updated successfully",
        "whatsapp_link": app_settings.whatsapp_link
    }
