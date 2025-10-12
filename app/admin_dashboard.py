from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, date
import os

from .core.database import get_db
from app.models.database_models import User, Order, OrderItem, MenuItem, BankTransfer, MenuCategory
from app.models.database_models import OrderStatus as OrderStatusEnum
from app.models.database_models import PaymentStatus as PaymentStatusEnum
from app.models.database_models import UserRole

# Create admin router
admin_router = APIRouter()

# Setup templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)

templates = Jinja2Templates(directory=templates_dir)

# Database-connected functions (replacing mock data)
def get_dashboard_stats(db: Session):
    today = date.today()

    total_users = db.query(User).filter(User.role == UserRole.CUSTOMER).count()
    total_orders = db.query(Order).count()
    total_menu_items = db.query(MenuItem).count()
    today_orders = db.query(Order).filter(
        func.date(Order.created_at) == today
    ).count()

    pending_orders = db.query(Order).filter(
        Order.status.in_(["pending_payment", "payment_confirmed", "preparing"])
    ).count()

    completed_orders = db.query(Order).filter(
        Order.status == "completed"
    ).count()

    total_revenue = db.query(func.sum(Order.total_amount)).filter(
        Order.payment_status == "completed"
    ).scalar() or 0

    today_revenue = db.query(func.sum(Order.total_amount)).filter(
        func.date(Order.created_at) == today,
        Order.payment_status == "completed"
    ).scalar() or 0

    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_menu_items": total_menu_items,
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_revenue": float(total_revenue),
        "today_revenue": float(today_revenue)
    }

def get_recent_orders(db: Session, limit: int = 20):
    orders = db.query(Order).options(
        joinedload(Order.customer),
        joinedload(Order.order_items).joinedload(OrderItem.menu_item)
    ).order_by(desc(Order.created_at)).limit(limit).all()

    result = []
    for order in orders:
        # Get order items summary
        items_summary = ", ".join([
            f"{item.quantity}x {item.menu_item.name}"
            for item in order.order_items
        ]) if order.order_items else "No items"

        result.append({
            "id": order.id,
            "order_number": order.order_number,
            "customer": f"{order.customer.first_name} {order.customer.last_name}" if order.customer else order.customer_name,
            "customer_email": order.customer.email if order.customer else order.customer_email,
            "items": items_summary,
            "total": order.total_amount,
            "status": order.status,  # Already a string
            "payment_status": order.payment_status,  # Already a string
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return result

def get_menu_items_from_db(db: Session):
    menu_items = db.query(MenuItem).join(MenuCategory).order_by(MenuItem.name).all()

    result = []
    for item in menu_items:
        result.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "category": item.category.name,
            "price": item.price,
            "available": item.is_available,
            "is_featured": item.is_featured,
            "preparation_time": item.preparation_time,
            "created_at": item.created_at.strftime("%Y-%m-%d")
        })

    return result

def get_users_from_db(db: Session):
    users = db.query(User).order_by(desc(User.created_at)).all()

    result = []
    for user in users:
        result.append({
            "id": user.id,
            "name": f"{user.first_name} {user.last_name}",
            "email": user.email,
            "phone": user.phone,
            "role": user.role,  # Already a string
            "active": user.is_active,
            "email_verified": user.is_verified,
            "created_at": user.created_at.strftime("%Y-%m-%d")
        })

    return result

# Admin authentication check (basic example)
def get_current_admin_user(request: Request):
    # Check if admin is logged in (basic session check)
    admin_session = request.session.get("admin_logged_in")
    if not admin_session:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return {"username": "admin", "role": "admin"}

# Admin routes
@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    """Admin Dashboard - Overview of restaurant operations"""
    stats = get_dashboard_stats(db)
    recent_orders = get_recent_orders(db, limit=10)

    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_orders": recent_orders,
        "page_title": "Admin Dashboard",
        "admin_user": admin_user
    })

@admin_router.get("/orders", response_class=HTMLResponse)
async def admin_orders(request: Request, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    """Order Management - View and manage all orders"""
    orders = get_recent_orders(db, limit=50)  # Get more orders for management

    return templates.TemplateResponse("admin_orders.html", {
        "request": request,
        "orders": orders,
        "page_title": "Order Management",
        "admin_user": admin_user
    })

@admin_router.get("/menu", response_class=HTMLResponse)
async def admin_menu(request: Request, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    """Menu Management - Manage restaurant menu items"""
    menu_items = get_menu_items_from_db(db)

    return templates.TemplateResponse("admin_menu.html", {
        "request": request,
        "menu_items": menu_items,
        "page_title": "Menu Management",
        "admin_user": admin_user
    })

@admin_router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    """User Management - Manage customer and staff accounts"""
    users = get_users_from_db(db)

    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "users": users,
        "page_title": "User Management",
        "admin_user": admin_user
    })

@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: Session = Depends(get_db), admin_user=Depends(get_current_admin_user)):
    """Settings - Configure WhatsApp and app settings"""
    from app.models.database_models import AppSettings

    # Get or create settings
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return templates.TemplateResponse("admin_settings.html", {
        "request": request,
        "settings": settings,
        "page_title": "Settings",
        "admin_user": admin_user
    })

@admin_router.post("/settings")
async def admin_settings_update(
    request: Request,
    whatsapp_link: str = Form(...),
    whatsapp_enabled: bool = Form(False),
    restaurant_name: str = Form(...),
    restaurant_phone: str = Form(...),
    restaurant_email: str = Form(...),
    restaurant_address: str = Form(...),
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Update Settings"""
    from app.models.database_models import AppSettings

    # Get or create settings
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)

    # Update settings
    settings.whatsapp_link = whatsapp_link
    settings.whatsapp_enabled = whatsapp_enabled
    settings.restaurant_name = restaurant_name
    settings.restaurant_phone = restaurant_phone
    settings.restaurant_email = restaurant_email
    settings.restaurant_address = restaurant_address
    settings.updated_at = datetime.utcnow()

    db.commit()

    # Redirect back to settings with success message
    return RedirectResponse(url="/admin/settings?success=true", status_code=303)

@admin_router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin Login Page"""
    return templates.TemplateResponse("admin_login.html", {
        "request": request,
        "page_title": "Admin Login"
    })

@admin_router.post("/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Handle admin login"""
    from app.auth.auth import AuthService

    # Find user by email (username field is used for email)
    user = db.query(User).filter(User.email == username).first()

    # Check if user exists, is admin, and password is correct
    if (user and
        user.role == UserRole.ADMIN.value and
        user.hashed_password and
        AuthService.verify_password(password, user.hashed_password)):
        request.session["admin_logged_in"] = True
        request.session["admin_username"] = user.email
        request.session["admin_user_id"] = user.id
        return RedirectResponse(url="/admin", status_code=303)
    else:
        return templates.TemplateResponse("admin_login.html", {
            "request": request,
            "error": "Invalid credentials",
            "page_title": "Admin Login"
        })

@admin_router.post("/logout")
async def admin_logout(request: Request):
    """Handle admin logout"""
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=303)

# API endpoints for admin operations
@admin_router.post("/api/orders/{order_id}/update-status")
async def update_order_status(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Update order status"""
    from app.websockets import notify_order_status_change

    try:
        # Get the new status from request body
        body = await request.json()
        new_status = body.get("status")

        # Validate status
        valid_statuses = [status.value for status in OrderStatusEnum]
        if new_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status")

        # Find and update the order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update the status
        order.status = new_status
        order.updated_at = datetime.utcnow()

        # Set ready time if status is READY_FOR_PICKUP
        if new_status == "ready_for_pickup":
            order.actual_ready_time = datetime.utcnow()

        db.commit()

        # Send real-time notification to customer
        await notify_order_status_change(
            order_id=order.id,
            customer_id=order.customer_id,
            new_status=new_status,
            order_number=order.order_number
        )

        return {"message": f"Order {order_id} status updated to {new_status}", "success": True}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/api/orders/{order_id}/update-payment-status")
async def update_payment_status(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Update order payment status"""
    from app.websockets import notify_payment_status_change, notify_order_status_change

    try:
        # Get the new payment status from request body
        body = await request.json()
        new_payment_status = body.get("payment_status")

        # Validate payment status
        valid_statuses = [status.value for status in PaymentStatusEnum]
        if new_payment_status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid payment status")

        # Find and update the order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Update the payment status
        order.payment_status = new_payment_status
        order.updated_at = datetime.utcnow()

        # If payment completed, also update order status if still pending
        order_status_changed = False
        if new_payment_status == "completed" and order.status == "pending_payment":
            order.status = "payment_confirmed"
            order_status_changed = True

        db.commit()

        # Send real-time notifications to customer
        await notify_payment_status_change(
            order_id=order.id,
            customer_id=order.customer_id,
            payment_status=new_payment_status,
            order_number=order.order_number
        )

        # Also notify about order status change if it changed
        if order_status_changed:
            await notify_order_status_change(
                order_id=order.id,
                customer_id=order.customer_id,
                new_status="payment_confirmed",
                order_number=order.order_number
            )

        return {"message": f"Order {order_id} payment status updated to {new_payment_status}", "success": True}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.get("/api/orders/{order_id}/payment-proof")
async def get_payment_proof(
    order_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Get payment proof for an order"""
    try:
        # Find the bank transfer record
        bank_transfer = db.query(BankTransfer).filter(BankTransfer.order_id == order_id).first()

        if not bank_transfer:
            raise HTTPException(status_code=404, detail="No payment proof found for this order")

        return {
            "order_id": order_id,
            "reference_number": bank_transfer.reference_number,
            "amount": bank_transfer.amount,
            "sender_name": bank_transfer.sender_name,
            "sender_account": bank_transfer.sender_account,
            "transfer_date": bank_transfer.transfer_date.isoformat() if bank_transfer.transfer_date else None,
            "receipt_image_url": bank_transfer.receipt_image_url,
            "verification_status": bank_transfer.verification_status,
            "notes": bank_transfer.notes,
            "created_at": bank_transfer.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/api/menu/{item_id}/toggle-availability")
async def toggle_menu_availability(
    item_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Toggle menu item availability"""
    try:
        # Find the menu item
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Toggle availability
        menu_item.is_available = not menu_item.is_available
        menu_item.updated_at = datetime.utcnow()

        db.commit()

        status_text = "available" if menu_item.is_available else "unavailable"
        return {"message": f"Menu item '{menu_item.name}' is now {status_text}", "success": True, "available": menu_item.is_available}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/api/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Toggle user active status"""
    try:
        # Find the user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Don't allow disabling admin users
        if user.role == "admin":
            raise HTTPException(status_code=403, detail="Cannot disable admin users")

        # Toggle active status
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()

        db.commit()

        status_text = "activated" if user.is_active else "deactivated"
        return {"message": f"User '{user.full_name}' has been {status_text}", "success": True, "active": user.is_active}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Additional API endpoints for full CRUD operations
@admin_router.post("/api/menu/items")
async def create_menu_item(
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Create a new menu item"""
    try:
        data = await request.json()

        # Check if category exists
        category = db.query(MenuCategory).filter(MenuCategory.name == data.get("category")).first()
        if not category:
            # Create category if it doesn't exist
            category = MenuCategory(name=data.get("category"), is_active=True)
            db.add(category)
            db.flush()

        # Create menu item
        menu_item = MenuItem(
            name=data.get("name"),
            description=data.get("description"),
            price=float(data.get("price")),
            category_id=category.id,
            is_available=data.get("available", True),
            image_url=data.get("image_url"),
            preparation_time=data.get("preparation_time", 15)
        )

        db.add(menu_item)
        db.commit()

        return {"message": f"Menu item '{menu_item.name}' created successfully", "success": True, "item_id": menu_item.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.put("/api/menu/items/{item_id}")
async def update_menu_item(
    item_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Update an existing menu item"""
    try:
        data = await request.json()

        # Find the menu item
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Update fields
        if "name" in data:
            menu_item.name = data["name"]
        if "description" in data:
            menu_item.description = data["description"]
        if "price" in data:
            menu_item.price = float(data["price"])
        if "available" in data:
            menu_item.is_available = data["available"]
        if "image_url" in data:
            menu_item.image_url = data["image_url"]
        if "preparation_time" in data:
            menu_item.preparation_time = data["preparation_time"]

        menu_item.updated_at = datetime.utcnow()
        db.commit()

        return {"message": f"Menu item '{menu_item.name}' updated successfully", "success": True}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.delete("/api/menu/items/{item_id}")
async def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    """Delete a menu item"""
    try:
        # Find the menu item
        menu_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Check if item has existing orders
        has_orders = db.query(OrderItem).filter(OrderItem.menu_item_id == item_id).first()
        if has_orders:
            # Don't delete, just make unavailable
            menu_item.is_available = False
            menu_item.updated_at = datetime.utcnow()
            db.commit()
            return {"message": f"Menu item '{menu_item.name}' marked as unavailable (has existing orders)", "success": True}
        else:
            # Safe to delete
            db.delete(menu_item)
            db.commit()
            return {"message": f"Menu item deleted successfully", "success": True}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
