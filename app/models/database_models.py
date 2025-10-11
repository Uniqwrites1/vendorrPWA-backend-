"""
SQLAlchemy database models for Vendorr PWA
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
import enum
from datetime import datetime


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PREPARING = "preparing"
    ALMOST_READY = "almost_ready"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    KITCHEN = "kitchen"
    COUNTER = "counter"
    ADMIN = "admin"


# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    role = Column(String(13), default="customer")  # Using string to match DB
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    profile_image = Column(String(255))
    google_id = Column(String(100), unique=True, index=True)
    facebook_id = Column(String(100), unique=True, index=True)
    dietary_preferences = Column(Text)
    notification_preferences = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


# Menu Category Model
class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    icon = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    menu_items = relationship("MenuItem", back_populates="category")


# Menu Item Model
class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("menu_categories.id"))
    image_url = Column(String(255))
    thumbnail_url = Column(String(255))
    calories = Column(Integer)
    ingredients = Column(Text)  # JSON string
    allergens = Column(Text)  # JSON string
    dietary_tags = Column(Text)  # JSON string
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    status = Column(String(12))
    preparation_time = Column(Integer, default=15)  # minutes
    spice_level = Column(Integer)
    customizable = Column(Boolean, default=False)
    customization_options = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("MenuCategory", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")
    reviews = relationship("Review", back_populates="menu_item")


# Order Model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(17), default="pending_payment")  # Using string to match DB
    payment_status = Column(String(9), default="pending")  # Using string to match DB
    subtotal = Column(Float, default=0)
    tax_amount = Column(Float, default=0)
    tip_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    customer_email = Column(String(255))
    notes = Column(Text)
    estimated_ready_time = Column(DateTime(timezone=True))
    actual_ready_time = Column(DateTime(timezone=True))
    payment_method = Column(String(50))
    payment_reference = Column(String(100))
    bank_transfer_receipt = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="order")


# Order Item Model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    customizations = Column(Text)  # JSON string
    notes = Column(Text)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


# Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))  # Using 'customer_id' instead of 'user_id'
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    is_verified = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews", foreign_keys=[customer_id])
    menu_item = relationship("MenuItem", back_populates="reviews")


# Notification Model
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))  # Using 'type' instead of 'notification_type'
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    push_notification_data = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="notifications")
    order = relationship("Order", back_populates="notifications")


# Bank Transfer Model
class BankTransfer(Base):
    __tablename__ = "bank_transfer_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    sender_name = Column(String(200))
    transfer_amount = Column(Float, nullable=False)
    transfer_date = Column(DateTime(timezone=True))
    reference_number = Column(String(100))
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
    confirmation_notes = Column(Text)
    receipt_image_path = Column(String(255))
    is_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
