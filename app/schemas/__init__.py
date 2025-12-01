from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums matching the database models
class UserRole(str, Enum):
    CUSTOMER = "customer"
    KITCHEN_STAFF = "kitchen_staff"
    COUNTER_STAFF = "counter_staff"
    MANAGER = "manager"
    ADMIN = "admin"

class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PREPARING = "preparing"
    ALMOST_READY = "almost_ready"
    READY_FOR_PICKUP = "ready_for_pickup"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"

class MenuItemStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    OUT_OF_STOCK = "out_of_stock"

# Base schemas
class BaseSchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "use_enum_values": True
    }

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    phone: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: UserRole = UserRole.CUSTOMER

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if info.data and 'password' in info.data and v != info.data['password']:
            raise ValueError('passwords do not match')
        return v

class UserUpdate(BaseSchema):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    dietary_preferences: Optional[Dict[str, Any]] = None
    notification_preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class UserLogin(BaseSchema):
    email: EmailStr
    password: str

# Token schemas
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseSchema):
    user_id: Optional[str] = None
    email: Optional[str] = None

# OAuth schemas
class OAuthRequest(BaseSchema):
    provider: str = Field(..., pattern="^(google|facebook)$")
    token: str = Field(..., min_length=1)
    device_info: Optional[Dict[str, Any]] = None

# Menu Category schemas
class MenuCategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True
    icon: Optional[str] = None

class MenuCategoryCreate(MenuCategoryBase):
    pass

class MenuCategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None

class MenuCategoryResponse(MenuCategoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Menu Item schemas
class MenuItemBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: int
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    spice_level: Optional[int] = Field(0, ge=0, le=5)
    status: MenuItemStatus = MenuItemStatus.AVAILABLE
    prep_time_minutes: int = Field(15, ge=1, le=180)
    is_daily_special: bool = False
    customization_options: Optional[Dict[str, Any]] = None

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0)
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    dietary_tags: Optional[List[str]] = None
    spice_level: Optional[int] = Field(None, ge=0, le=5)
    status: Optional[MenuItemStatus] = None
    prep_time_minutes: Optional[int] = Field(None, ge=1, le=180)
    is_daily_special: Optional[bool] = None
    customization_options: Optional[Dict[str, Any]] = None

class MenuItemResponse(MenuItemBase):
    id: int
    category: MenuCategoryResponse
    popularity_score: float = Field(0.0, description="Popularity score (default 0.0)")
    total_orders: int = Field(0, description="Total orders count (default 0)")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Order Item schemas
class OrderItemBase(BaseSchema):
    menu_item_id: int
    quantity: int = Field(..., ge=1, le=50)
    customizations: Optional[Dict[str, Any]] = None
    special_instructions: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    unit_price: float
    total_price: float
    menu_item: MenuItemResponse
    created_at: Optional[datetime] = None

# Order schemas
class OrderBase(BaseSchema):
    order_type: str = "pickup"
    scheduled_time: Optional[datetime] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    special_instructions: Optional[str] = None
    promo_code: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_items=1)
    payment_method: Optional[str] = "bank_transfer"
    payment_reference: Optional[str] = None
    bank_transfer_receipt: Optional[str] = None

class OrderUpdate(BaseSchema):
    status: Optional[OrderStatus] = None
    estimated_prep_time: Optional[int] = None
    ready_time: Optional[datetime] = None
    pickup_time: Optional[datetime] = None

class OrderResponse(BaseSchema):
    id: int
    order_number: str
    customer_id: int
    status: str  # OrderStatus enum as string
    payment_status: Optional[str] = None
    subtotal: float
    tax_amount: float
    tip_amount: Optional[float] = 0.0
    total_amount: float
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    notes: Optional[str] = None
    estimated_ready_time: Optional[datetime] = None
    actual_ready_time: Optional[datetime] = None
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    bank_transfer_receipt: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Optional relationships - will be loaded if needed
    items: Optional[List[OrderItemResponse]] = Field(default=[], alias="order_items")
    customer: Optional[UserResponse] = None

    class Config:
        populate_by_name = True  # Allow both "items" and "order_items"

# Payment schemas
class PaymentBase(BaseSchema):
    amount: float = Field(..., gt=0)
    payment_method: str = "bank_transfer"
    transfer_reference: Optional[str] = None
    bank_account_last_4: Optional[str] = Field(None, min_length=4, max_length=4)

class PaymentCreate(PaymentBase):
    order_id: int

class PaymentProofUpload(BaseSchema):
    payment_id: int
    proof_of_payment_url: str

class PaymentConfirmation(BaseSchema):
    payment_id: int
    confirmation_notes: Optional[str] = None

class PaymentRejection(BaseSchema):
    payment_id: int
    rejection_reason: str = Field(..., min_length=1)

class PaymentResponse(PaymentBase):
    id: int
    order_id: int
    status: PaymentStatus
    proof_of_payment_url: Optional[str] = None
    confirmed_by: Optional[int] = None
    confirmation_notes: Optional[str] = None
    confirmed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Notification schemas
class NotificationBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: str
    metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: str
    order_id: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: str
    order_id: Optional[int] = None
    is_read: bool
    is_push_sent: bool
    push_sent_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

# Review schemas
class ReviewBase(BaseSchema):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    photos: Optional[List[str]] = None

class ReviewCreate(ReviewBase):
    menu_item_id: Optional[int] = None
    order_id: Optional[int] = None

class ReviewResponse(ReviewBase):
    id: int
    customer_id: str
    menu_item_id: Optional[int] = None
    order_id: Optional[int] = None
    is_approved: bool
    is_featured: bool
    customer: UserResponse
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Staff Account schemas
class StaffAccountBase(BaseSchema):
    employee_id: Optional[str] = None
    department: Optional[str] = None
    shift_start: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    shift_end: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    permissions: Optional[Dict[str, Any]] = None

class StaffAccountCreate(StaffAccountBase):
    user_id: str

class StaffAccountResponse(StaffAccountBase):
    id: int
    user_id: str
    is_on_duty: bool
    last_activity: Optional[datetime] = None
    user: UserResponse
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# API Response wrappers
class APIResponse(BaseSchema):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None

class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int = 1
    size: int = 10
    pages: int

class ErrorResponse(BaseSchema):
    success: bool = False
    message: str
    errors: Optional[List[Dict[str, Any]]] = None
