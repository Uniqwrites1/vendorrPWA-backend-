from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# Enums for database
class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    KITCHEN_STAFF = "kitchen_staff"
    COUNTER_STAFF = "counter_staff"
    MANAGER = "manager"
    ADMIN = "admin"

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
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class MenuItemStatus(str, enum.Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    OUT_OF_STOCK = "out_of_stock"

# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    profile_image = Column(String(255))

    # OAuth fields
    google_id = Column(String(100))
    facebook_id = Column(String(100))

    # Preferences
    dietary_preferences = Column(Text)  # JSON string
    notification_preferences = Column(Text)  # JSON string

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")

# Menu Category Model
class MenuCategory(Base):
    __tablename__ = "menu_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    icon = Column(String(100))  # Icon name or emoji

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
    category_id = Column(Integer, ForeignKey("menu_categories.id"), nullable=False)

    # Images
    image_url = Column(String(255))
    thumbnail_url = Column(String(255))

    # Nutritional and dietary info
    calories = Column(Integer)
    ingredients = Column(Text)  # JSON string
    allergens = Column(Text)  # JSON string
    dietary_tags = Column(Text)  # JSON string (vegetarian, vegan, gluten-free, etc.)

    # Availability
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    status = Column(SQLEnum(MenuItemStatus), default=MenuItemStatus.AVAILABLE)

    # Preparation info
    preparation_time = Column(Integer)  # in minutes
    spice_level = Column(Integer)  # 0-5 scale

    # Customization options
    customizable = Column(Boolean, default=False)
    customization_options = Column(Text)  # JSON string

    # Timestamps
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
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Order status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING_PAYMENT, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

    # Pricing
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0)
    tip_amount = Column(Float, default=0)
    total_amount = Column(Float, nullable=False)

    # Customer info (for guests or extra info)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    customer_email = Column(String(255))

    # Order details
    notes = Column(Text)
    estimated_ready_time = Column(DateTime(timezone=True))
    actual_ready_time = Column(DateTime(timezone=True))

    # Payment info
    payment_method = Column(String(50))  # "bank_transfer", "card", "cash"
    payment_reference = Column(String(100))
    bank_transfer_receipt = Column(String(255))  # File path for receipt image

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")
    bank_transfer_confirmation = relationship("BankTransferConfirmation", back_populates="order", uselist=False)

# Order Item Model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Customizations
    customizations = Column(Text)  # JSON string
    notes = Column(Text)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

# Bank Transfer Confirmation Model
class BankTransferConfirmation(Base):
    __tablename__ = "bank_transfer_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Transfer details
    sender_name = Column(String(200), nullable=False)
    transfer_amount = Column(Float, nullable=False)
    transfer_date = Column(DateTime(timezone=True), nullable=False)
    reference_number = Column(String(100))

    # Confirmation details
    confirmed_by = Column(Integer, ForeignKey("users.id"))
    confirmed_at = Column(DateTime(timezone=True))
    confirmation_notes = Column(Text)

    # Receipt image
    receipt_image_path = Column(String(255))

    # Status
    is_confirmed = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order = relationship("Order", back_populates="bank_transfer_confirmation")

# Notification Model
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"))

    # Notification content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))  # "order_update", "promotion", "system", etc.

    # Status
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)

    # Push notification data
    push_notification_data = Column(Text)  # JSON string for extra data

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User")
    order = relationship("Order")

# Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"))
    order_id = Column(Integer, ForeignKey("orders.id"))

    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)

    # Review metadata
    is_verified = Column(Boolean, default=False)  # Customer actually ordered the item
    is_featured = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("User", back_populates="reviews")
    menu_item = relationship("MenuItem", back_populates="reviews")
    order = relationship("Order")

# Admin Settings Model
class AdminSettings(Base):
    __tablename__ = "admin_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Restaurant settings
    restaurant_name = Column(String(200))
    restaurant_phone = Column(String(20))
    restaurant_email = Column(String(255))
    restaurant_address = Column(Text)

    # Business hours
    business_hours = Column(Text)  # JSON string

    # Bank details
    bank_name = Column(String(200))
    bank_account_number = Column(String(100))
    bank_account_name = Column(String(200))

    # Notification settings
    notification_settings = Column(Text)  # JSON string

    # Other settings
    extra_data = Column(Text)  # JSON string for extra data

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
