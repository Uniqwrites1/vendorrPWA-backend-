"""
Database service functions for Vendorr PWA
Replaces mock data with real database operations
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta
import json

from ..models.database_models import *
from ..core.database import get_db
from ..schemas import *


class DatabaseService:
    """Service class for database operations"""

    def __init__(self, db: Session):
        self.db = db

    # User operations
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()

    # Menu operations
    def get_menu_categories(self) -> List[MenuCategory]:
        """Get all active menu categories"""
        return self.db.query(MenuCategory).filter(
            MenuCategory.is_active == True
        ).order_by(MenuCategory.sort_order).all()

    def get_menu_items(self, category_id: Optional[int] = None) -> List[MenuItem]:
        """Get menu items, optionally filtered by category"""
        query = self.db.query(MenuItem).options(joinedload(MenuItem.category))

        if category_id:
            query = query.filter(MenuItem.category_id == category_id)

        return query.filter(MenuItem.is_available == True).order_by(
            MenuItem.sort_order, MenuItem.name
        ).all()

    def get_menu_item_by_id(self, item_id: int) -> Optional[MenuItem]:
        """Get menu item by ID"""
        return self.db.query(MenuItem).options(joinedload(MenuItem.category)).filter(
            MenuItem.id == item_id
        ).first()

    def get_featured_items(self) -> List[MenuItem]:
        """Get featured menu items"""
        return self.db.query(MenuItem).options(joinedload(MenuItem.category)).filter(
            MenuItem.is_featured == True,
            MenuItem.is_available == True
        ).order_by(MenuItem.sort_order).all()

    # Order operations
    def create_order(self, order_data: dict, order_items: List[dict]) -> Order:
        """Create a new order with items"""
        # Generate order number
        last_order = self.db.query(Order).order_by(desc(Order.id)).first()
        order_number = f"ORD-{(last_order.id + 1):04d}" if last_order else "ORD-0001"

        order_data['order_number'] = order_number
        order = Order(**order_data)
        self.db.add(order)
        self.db.flush()  # Get the order ID

        # Add order items
        for item_data in order_items:
            item_data['order_id'] = order.id
            order_item = OrderItem(**item_data)
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with all related data"""
        return self.db.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(Order.id == order_id).first()

    def get_order_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        return self.db.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(Order.order_number == order_number).first()

    def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 50) -> List[Order]:
        """Get orders for a specific user"""
        return self.db.query(Order).options(
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        ).filter(Order.customer_id == user_id).order_by(
            desc(Order.created_at)
        ).offset(skip).limit(limit).all()

    def get_all_orders(self, skip: int = 0, limit: int = 100, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get all orders with optional status filter"""
        query = self.db.query(Order).options(
            joinedload(Order.customer),
            joinedload(Order.order_items).joinedload(OrderItem.menu_item)
        )

        if status:
            query = query.filter(Order.status == status)

        return query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()

    def update_order_status(self, order_id: int, status: OrderStatus) -> Optional[Order]:
        """Update order status"""
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status
            order.updated_at = datetime.utcnow()

            if status == OrderStatus.READY:
                order.actual_ready_time = datetime.utcnow()

            self.db.commit()
            self.db.refresh(order)
        return order

    # Notification operations
    def create_notification(self, notification_data: dict) -> Notification:
        """Create a new notification"""
        notification = Notification(**notification_data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(desc(Notification.created_at)).all()

    def mark_notification_read(self, notification_id: int) -> Optional[Notification]:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification

    # Review operations
    def create_review(self, review_data: dict) -> Review:
        """Create a new review"""
        review = Review(**review_data)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_menu_item_reviews(self, menu_item_id: int) -> List[Review]:
        """Get reviews for a menu item"""
        return self.db.query(Review).options(joinedload(Review.user)).filter(
            Review.menu_item_id == menu_item_id
        ).order_by(desc(Review.created_at)).all()

    # Statistics and analytics
    def get_order_stats(self) -> dict:
        """Get order statistics for dashboard"""
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)

        # Total orders today
        orders_today = self.db.query(Order).filter(
            func.date(Order.created_at) == today
        ).count()

        # Total revenue today
        revenue_today = self.db.query(func.sum(Order.total_amount)).filter(
            func.date(Order.created_at) == today
        ).scalar() or 0

        # Pending orders
        pending_orders = self.db.query(Order).filter(
            Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING])
        ).count()

        # Orders this week
        orders_week = self.db.query(Order).filter(
            Order.created_at >= week_ago
        ).count()

        # Revenue this week
        revenue_week = self.db.query(func.sum(Order.total_amount)).filter(
            Order.created_at >= week_ago
        ).scalar() or 0

        # Popular items
        popular_items = self.db.query(
            MenuItem.name,
            func.sum(OrderItem.quantity).label('total_ordered')
        ).join(OrderItem).group_by(MenuItem.id, MenuItem.name).order_by(
            desc('total_ordered')
        ).limit(5).all()

        return {
            "orders_today": orders_today,
            "revenue_today": float(revenue_today),
            "pending_orders": pending_orders,
            "orders_week": orders_week,
            "revenue_week": float(revenue_week),
            "popular_items": [{"name": item.name, "count": item.total_ordered} for item in popular_items]
        }

    def get_daily_revenue(self, days: int = 7) -> List[dict]:
        """Get daily revenue for the last N days"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)

        daily_revenue = self.db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('orders')
        ).filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date
        ).group_by(func.date(Order.created_at)).all()

        return [
            {
                "date": str(day.date),
                "revenue": float(day.revenue or 0),
                "orders": day.orders
            }
            for day in daily_revenue
        ]


# Convenience function to get database service
def get_db_service(db: Session = None) -> DatabaseService:
    """Get database service instance"""
    if db is None:
        db = next(get_db())
    return DatabaseService(db)
