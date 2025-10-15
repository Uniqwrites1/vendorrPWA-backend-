"""
Real database operations to replace mock data in routers
"""
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
import json

from ..core.database import get_db
from ..models.database_models import User, Order, MenuItem, MenuCategory, OrderItem, Notification
from ..schemas import *


# Authentication functions
def get_current_user(db: Session = Depends(get_db), token: str = None) -> User:
    """Get current authenticated user"""
    # For now, return admin user for testing
    user = db.query(User).filter(User.email == "admin@vendorr.com").first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Menu operations
def get_menu_items_from_db(db: Session = Depends(get_db)) -> List[MenuItem]:
    """Get all available menu items from database"""
    return db.query(MenuItem).filter(MenuItem.is_available == True).all()


def get_menu_categories_from_db(db: Session = Depends(get_db)) -> List[MenuCategory]:
    """Get all menu categories from database"""
    return db.query(MenuCategory).filter(MenuCategory.is_active == True).all()


def get_featured_items_from_db(db: Session = Depends(get_db)) -> List[MenuItem]:
    """Get featured menu items from database"""
    return db.query(MenuItem).filter(
        MenuItem.is_featured == True,
        MenuItem.is_available == True
    ).all()


# Order operations
def create_order_in_db(order_data: dict, items: List[dict], db: Session = Depends(get_db)) -> Order:
    """Create a new order in database"""
    # Generate order number
    last_order = db.query(Order).order_by(desc(Order.id)).first()
    order_number = f"ORD-{(last_order.id + 1):04d}" if last_order else "ORD-0001"

    order_data['order_number'] = order_number
    order = Order(**order_data)
    db.add(order)
    db.flush()  # Get order ID

    # Add order items
    for item in items:
        item['order_id'] = order.id
        order_item = OrderItem(**item)
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


def get_orders_from_db(db: Session = Depends(get_db), limit: int = 50) -> List[Order]:
    """Get orders from database"""
    return db.query(Order).order_by(desc(Order.created_at)).limit(limit).all()


def get_order_by_id_from_db(order_id: int, db: Session = Depends(get_db)) -> Optional[Order]:
    """Get order by ID from database"""
    return db.query(Order).filter(Order.id == order_id).first()


def update_order_status_in_db(order_id: int, status: str, db: Session = Depends(get_db)) -> Optional[Order]:
    """Update order status in database"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if order:
        order.status = status
        order.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(order)
    return order


# User operations
def get_users_from_db(db: Session = Depends(get_db)) -> List[User]:
    """Get all users from database"""
    return db.query(User).all()


def get_user_by_id_from_db(user_id: int, db: Session = Depends(get_db)) -> Optional[User]:
    """Get user by ID from database"""
    return db.query(User).filter(User.id == user_id).first()


# Statistics
def get_dashboard_stats_from_db(db: Session = Depends(get_db)) -> dict:
    """Get dashboard statistics from database"""
    today = datetime.utcnow().date()

    # Orders today
    orders_today = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()

    # Revenue today
    revenue_today = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today
    ).scalar() or 0

    # Pending orders
    pending_orders = db.query(Order).filter(
        Order.status.in_(["pending", "confirmed", "preparing"])
    ).count()

    # Total customers
    total_customers = db.query(User).filter(User.role == "customer").count()

    return {
        "orders_today": orders_today,
        "revenue_today": float(revenue_today),
        "pending_orders": pending_orders,
        "total_customers": total_customers
    }
