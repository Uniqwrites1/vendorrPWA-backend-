from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..models import MenuCategory, MenuItem, MenuItemStatus
from ..schemas import MenuCategoryResponse, MenuItemResponse
import json

router = APIRouter()

def serialize_menu_item(item: MenuItem) -> dict:
    """Serialize menu item with default values for missing fields"""
    item_dict = {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "category_id": item.category_id,
        "image_url": item.image_url,
        "thumbnail_url": getattr(item, 'thumbnail_url', None),
        "calories": item.calories,
        "ingredients": getattr(item, 'ingredients', []),
        "allergens": getattr(item, 'allergens', []),
        "dietary_tags": getattr(item, 'dietary_tags', []),
        "is_available": item.is_available,
        "is_featured": item.is_featured,
        "status": item.status,
        "preparation_time": item.preparation_time,
        "spice_level": getattr(item, 'spice_level', 1),
        "is_daily_special": getattr(item, 'is_daily_special', False),
        "customizable": getattr(item, 'customizable', False),
        "customization_options": None,
        "popularity_score": 4.0,  # Default value
        "total_orders": 0,  # Default value
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "category": item.category
    }

    # Parse JSON customization_options if it exists
    if hasattr(item, 'customization_options') and item.customization_options:
        try:
            item_dict["customization_options"] = json.loads(item.customization_options)
        except (json.JSONDecodeError, TypeError):
            item_dict["customization_options"] = None

    return item_dict

@router.get("/categories", response_model=List[MenuCategoryResponse])
async def get_menu_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all menu categories"""
    categories = (
        db.query(MenuCategory)
        .filter(MenuCategory.is_active == True)
        .order_by(MenuCategory.display_order, MenuCategory.name)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return categories

@router.get("/categories/{category_id}", response_model=MenuCategoryResponse)
async def get_menu_category(category_id: int, db: Session = Depends(get_db)):
    """Get a specific menu category"""
    category = db.query(MenuCategory).filter(MenuCategory.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.get("/items")
async def get_menu_items(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all menu items, optionally filtered by category"""
    from sqlalchemy.orm import joinedload

    query = (
        db.query(MenuItem)
        .options(joinedload(MenuItem.category))
        .filter(MenuItem.status == "available")  # Use string comparison instead of enum
        .order_by(MenuItem.name)
    )

    if category_id:
        query = query.filter(MenuItem.category_id == category_id)

    items = query.offset(skip).limit(limit).all()

    # Serialize items with default values
    serialized_items = [serialize_menu_item(item) for item in items]
    return serialized_items

@router.get("/items/{item_id}", response_model=MenuItemResponse)
async def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """Get a specific menu item"""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )
    return item

@router.get("/featured", response_model=List[MenuItemResponse])
async def get_featured_items(db: Session = Depends(get_db)):
    """Get featured menu items (daily specials)"""
    items = (
        db.query(MenuItem)
        .filter(MenuItem.is_daily_special == True)
        .filter(MenuItem.status == "available")  # Use string comparison
        .order_by(MenuItem.popularity_score.desc())
        .limit(10)
        .all()
    )
    return items

@router.get("/popular", response_model=List[MenuItemResponse])
async def get_popular_items(limit: int = 10, db: Session = Depends(get_db)):
    """Get popular menu items"""
    items = (
        db.query(MenuItem)
        .filter(MenuItem.status == "available")  # Use string comparison
        .order_by(MenuItem.popularity_score.desc(), MenuItem.total_orders.desc())
        .limit(limit)
        .all()
    )
    return items
