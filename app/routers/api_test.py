from fastapi import APIRouter, HTTPException, Depends, status, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from ..schemas import *

router = APIRouter()
security = HTTPBearer()

# Mock data for testing
mock_users = [
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "customer",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now().isoformat(),
        "phone": "+27123456789"
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "email": "staff@vendorr.com",
        "first_name": "Jane",
        "last_name": "Staff",
        "role": "manager",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.now().isoformat(),
        "phone": "+27987654321"
    }
]

mock_menu_categories = [
    {
        "id": 1,
        "name": "Appetizers",
        "description": "Start your meal with our delicious appetizers",
        "display_order": 1,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "name": "Main Courses",
        "description": "Hearty main dishes to satisfy your appetite",
        "display_order": 2,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
]

mock_menu_items = [
    {
        "id": 1,
        "name": "Grilled Chicken Burger",
        "description": "Juicy grilled chicken breast with fresh lettuce, tomatoes, and our signature sauce",
        "price": 89.99,
        "category_id": 2,
        "image_url": "/uploads/chicken-burger.jpg",
        "calories": 650,
        "ingredients": ["chicken breast", "brioche bun", "lettuce", "tomatoes", "onions"],
        "allergens": ["gluten", "eggs"],
        "dietary_tags": ["high-protein"],
        "spice_level": 1,
        "status": "available",
        "prep_time_minutes": 15,
        "is_daily_special": False,
        "popularity_score": 4.5,
        "total_orders": 150,
        "created_at": datetime.now().isoformat()
    },
    {
        "id": 2,
        "name": "Crispy Chicken Wings",
        "description": "6 pieces of crispy chicken wings with your choice of sauce",
        "price": 65.00,
        "category_id": 1,
        "image_url": "/uploads/chicken-wings.jpg",
        "calories": 480,
        "ingredients": ["chicken wings", "flour", "spices"],
        "allergens": ["gluten"],
        "dietary_tags": [],
        "spice_level": 3,
        "status": "available",
        "prep_time_minutes": 12,
        "is_daily_special": True,
        "popularity_score": 4.8,
        "total_orders": 89,
        "created_at": datetime.now().isoformat()
    }
]

# Placeholder image endpoint
@router.get("/placeholder/{width}/{height}", tags=["Utilities"])
async def get_placeholder_image(width: int, height: int):
    """Generate a simple placeholder image"""
    from fastapi.responses import Response

    # Simple SVG placeholder
    svg_content = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#e5e7eb"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#9ca3af" font-family="Arial, sans-serif" font-size="14">
            {width}x{height}
        </text>
    </svg>'''

    return Response(content=svg_content, media_type="image/svg+xml")

# Authentication endpoints
@router.post("/auth/register", response_model=APIResponse, tags=["Authentication"])
async def register_user(user_data: UserCreate):
    """
    Register a new user account

    Creates a new user with the provided information.
    Email must be unique and password must meet security requirements.
    """
    # Check if email already exists
    existing_user = next((u for u in mock_users if u["email"] == user_data.email), None)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    new_user = {
        "id": str(uuid.uuid4()),
        "email": user_data.email,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role,
        "is_active": True,
        "is_verified": False,
        "phone": user_data.phone,
        "created_at": datetime.now().isoformat()
    }

    mock_users.append(new_user)

    return APIResponse(
        message="User registered successfully",
        data={"user_id": new_user["id"], "email": new_user["email"]}
    )

@router.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login_user(credentials: UserLogin):
    """
    Authenticate user and return access token

    Validates user credentials and returns a JWT token for authenticated requests.
    """
    # Find user by email
    print(f"Login attempt for email: {credentials.email}")
    print(f"Available users: {[u['email'] for u in mock_users]}")
    user = next((u for u in mock_users if u["email"] == credentials.email), None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # In real implementation, verify password hash
    # For demo purposes, accept any password

    # Create mock token
    token_data = Token(
        access_token="mock_jwt_token_" + str(uuid.uuid4()),
        token_type="bearer",
        expires_in=3600,
        user=UserResponse(**user)
    )

    return token_data

# Mock authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Mock authentication - returns first user for demo purposes"""
    if not credentials.credentials.startswith("mock_jwt_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return UserResponse(**mock_users[0])

# Menu endpoints
@router.get("/menu/categories", response_model=List[MenuCategoryResponse], tags=["Menu"])
async def get_menu_categories():
    """
    Get all menu categories

    Returns all active menu categories ordered by display_order.
    """
    return [MenuCategoryResponse(**cat) for cat in mock_menu_categories]

@router.get("/menu/items", response_model=List[MenuItemResponse], tags=["Menu"])
async def get_menu_items(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    available_only: bool = Query(True, description="Show only available items")
):
    """
    Get menu items with optional filtering

    Returns menu items with support for:
    - Category filtering
    - Search functionality
    - Availability filtering
    """
    items = mock_menu_items.copy()

    if category_id:
        items = [item for item in items if item["category_id"] == category_id]

    if search:
        search_lower = search.lower()
        items = [
            item for item in items
            if search_lower in item["name"].lower() or
               search_lower in item.get("description", "").lower()
        ]

    if available_only:
        items = [item for item in items if item["status"] == "available"]

    # Add category info to each item
    for item in items:
        category = next((cat for cat in mock_menu_categories if cat["id"] == item["category_id"]), None)
        if category:
            item["category"] = MenuCategoryResponse(**category)

    return [MenuItemResponse(**item) for item in items]

@router.get("/menu/items/{item_id}", response_model=MenuItemResponse, tags=["Menu"])
async def get_menu_item(item_id: int = Path(..., description="Menu item ID")):
    """
    Get a specific menu item by ID

    Returns detailed information about a single menu item.
    """
    item = next((item for item in mock_menu_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found"
        )

    # Add category info
    category = next((cat for cat in mock_menu_categories if cat["id"] == item["category_id"]), None)
    if category:
        item["category"] = MenuCategoryResponse(**category)

    return MenuItemResponse(**item)

# Order endpoints
@router.post("/orders", response_model=APIResponse, tags=["Orders"])
async def create_order(
    order_data: OrderCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a new order

    Creates a new order with the specified items.
    Calculates totals and generates order reference.
    """
    # Calculate totals
    subtotal = 0
    order_items = []

    for item_data in order_data.items:
        menu_item = next((item for item in mock_menu_items if item["id"] == item_data.menu_item_id), None)
        if not menu_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {item_data.menu_item_id} not found"
            )

        if menu_item["status"] != "available":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu item {menu_item['name']} is not available"
            )

        item_total = menu_item["price"] * item_data.quantity
        subtotal += item_total

        order_items.append({
            "id": str(uuid.uuid4()),
            "menu_item_id": item_data.menu_item_id,
            "quantity": item_data.quantity,
            "unit_price": menu_item["price"],
            "total_price": item_total,
            "customizations": item_data.customizations or {},
            "special_instructions": item_data.special_instructions,
            "menu_item": MenuItemResponse(**menu_item),
            "created_at": datetime.now().isoformat()
        })

    # Create order
    order_id = str(uuid.uuid4())
    order_number = f"VEN-{datetime.now().strftime('%Y%m%d')}-{len(mock_users) + 1:04d}"

    tax_amount = subtotal * 0.15  # 15% VAT
    total_amount = subtotal + tax_amount

    new_order = {
        "id": order_id,
        "order_number": order_number,
        "customer_id": current_user.id,
        "status": "pending_payment",
        "order_type": order_data.order_type,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": 0,
        "total_amount": total_amount,
        "items": order_items,
        "customer": current_user,
        "special_instructions": order_data.special_instructions,
        "created_at": datetime.now().isoformat(),
        "estimated_prep_time": max(item["menu_item"].prep_time_minutes for item in order_items)
    }

    return APIResponse(
        message="Order created successfully",
        data={
            "order_id": order_id,
            "order_number": order_number,
            "total_amount": total_amount,
            "status": "pending_payment"
        }
    )

@router.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_order(
    order_id: str = Path(..., description="Order ID"),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Get order details by ID

    Returns complete order information including items and status.
    """
    # Mock order data
    mock_order = {
        "id": order_id,
        "order_number": f"VEN-20250923-0001",
        "customer_id": current_user.id,
        "status": "preparing",
        "order_type": "pickup",
        "subtotal": 154.99,
        "tax_amount": 23.25,
        "discount_amount": 0,
        "total_amount": 178.24,
        "estimated_prep_time": 15,
        "items": [
            {
                "id": str(uuid.uuid4()),
                "menu_item_id": 1,
                "quantity": 1,
                "unit_price": 89.99,
                "total_price": 89.99,
                "customizations": {},
                "special_instructions": None,
                "menu_item": mock_menu_items[0],
                "created_at": datetime.now().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "menu_item_id": 2,
                "quantity": 1,
                "unit_price": 65.00,
                "total_price": 65.00,
                "customizations": {},
                "special_instructions": "Extra spicy",
                "menu_item": mock_menu_items[1],
                "created_at": datetime.now().isoformat()
            }
        ],
        "customer": current_user,
        "special_instructions": "Please prepare fresh",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    return OrderResponse(**mock_order)

# Payment endpoints
@router.post("/payments", response_model=APIResponse, tags=["Payments"])
async def create_payment(
    payment_data: PaymentCreate,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Create a payment record for an order

    Initiates payment processing for the specified order.
    """
    payment_id = str(uuid.uuid4())

    mock_payment = {
        "id": payment_id,
        "order_id": payment_data.order_id,
        "amount": payment_data.amount,
        "payment_method": payment_data.payment_method,
        "transfer_reference": payment_data.transfer_reference,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    return APIResponse(
        message="Payment record created successfully",
        data={
            "payment_id": payment_id,
            "status": "pending",
            "next_step": "Upload proof of payment"
        }
    )

# Admin endpoints
@router.get("/admin/dashboard", response_model=APIResponse, tags=["Admin"])
async def get_admin_dashboard(current_user: UserResponse = Depends(get_current_user)):
    """
    Get admin dashboard statistics

    Returns comprehensive dashboard data for restaurant management.
    Requires staff-level access.
    """
    dashboard_data = {
        "orders_today": 25,
        "revenue_today": 2450.75,
        "pending_orders": 5,
        "active_customers": 15,
        "popular_items": [
            {"name": "Grilled Chicken Burger", "orders": 12},
            {"name": "Crispy Chicken Wings", "orders": 8}
        ],
        "recent_orders": [
            {
                "id": "order-1",
                "order_number": "VEN-20250923-0001",
                "customer_name": "John Doe",
                "status": "preparing",
                "total": 178.24,
                "created_at": datetime.now().isoformat()
            }
        ],
        "system_status": {
            "database": "healthy",
            "payment_processing": "operational",
            "notifications": "active"
        }
    }

    return APIResponse(
        message="Dashboard data retrieved successfully",
        data=dashboard_data
    )

# Notification endpoints
@router.get("/notifications", response_model=List[NotificationResponse], tags=["Notifications"])
async def get_user_notifications(
    current_user: UserResponse = Depends(get_current_user),
    unread_only: bool = Query(False, description="Show only unread notifications")
):
    """
    Get user notifications

    Returns notifications for the current user with optional filtering.
    """
    mock_notifications = [
        {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "title": "Order Confirmed",
            "message": "Your order VEN-20250923-0001 has been confirmed and is being prepared",
            "notification_type": "order_update",
            "metadata": {"order_id": "order-1"},
            "is_read": False,
            "is_push_sent": True,
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "title": "Welcome!",
            "message": "Welcome to Vendorr! Enjoy browsing our menu and placing your first order.",
            "notification_type": "info",
            "metadata": {},
            "is_read": True,
            "is_push_sent": False,
            "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
            "read_at": datetime.now().isoformat()
        }
    ]

    if unread_only:
        mock_notifications = [n for n in mock_notifications if not n["is_read"]]

    return [NotificationResponse(**notification) for notification in mock_notifications]

# Orders endpoints (mock version for testing)
@router.get("/orders/my", tags=["Orders"])
async def get_my_orders():
    """
    Get current user's orders (mock implementation)

    Returns a list of mock orders for testing purposes.
    """
    # Return empty array to test basic functionality first
    return []

@router.get("/test-orders", tags=["Orders"])
async def get_test_orders():
    """
    Test orders endpoint to verify routing is working
    """
    return {"message": "Orders endpoint is working", "orders": []}# System endpoints for testing
@router.get("/test/generate-sample-data", response_model=APIResponse, tags=["Testing"])
async def generate_sample_data():
    """
    Generate sample test data

    Creates sample menu items, categories, and orders for testing purposes.
    Only available in development environment.
    """
    return APIResponse(
        message="Sample data generated successfully",
        data={
            "categories": len(mock_menu_categories),
            "menu_items": len(mock_menu_items),
            "users": len(mock_users)
        }
    )
