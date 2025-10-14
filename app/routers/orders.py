from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import json

from ..core.database import get_db
from ..models import Order, OrderItem, User
from ..models.database_models import MenuItem
from ..schemas import OrderCreate, OrderResponse, OrderUpdate
from ..auth.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    try:
        # Calculate totals
        subtotal = 0
        order_items_data = []

        for item_data in order_data.items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item_data.menu_item_id).first()
            if not menu_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Menu item with id {item_data.menu_item_id} not found"
                )

            if menu_item.status != "available":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Menu item '{menu_item.name}' is not available"
                )

            item_total = menu_item.price * item_data.quantity
            subtotal += item_total

            order_items_data.append({
                "menu_item_id": menu_item.id,
                "quantity": item_data.quantity,
                "unit_price": menu_item.price,
                "total_price": item_total,
                "customizations": json.dumps(item_data.customizations) if item_data.customizations else None,
                "notes": item_data.special_instructions
            })

        # Calculate tax and total
        tax_rate = 0.08  # 8% tax
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount

        # Generate order number
        order_count = db.query(Order).count() + 1
        order_number = f"ORD{order_count:06d}"

        # Create order - only use fields that exist in the Order model
        order = Order(
            order_number=order_number,
            customer_id=current_user.id,
            status="pending_payment",
            customer_name=order_data.customer_name or f"{current_user.first_name} {current_user.last_name}",
            customer_phone=order_data.customer_phone or current_user.phone,
            customer_email=order_data.customer_email or current_user.email,
            notes=order_data.special_instructions,  # Map special_instructions to notes field
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount
        )

        db.add(order)
        db.flush()  # Get the order ID

        # Create order items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                **item_data
            )
            db.add(order_item)

        db.commit()
        db.refresh(order)

        # Load relationships for the response
        order_with_relations = (
            db.query(Order)
            .options(joinedload(Order.order_items), joinedload(Order.customer))
            .filter(Order.id == order.id)
            .first()
        )

        # Send real-time notification to admin about new order
        from ..websockets import notify_admin_new_order
        await notify_admin_new_order(
            order_id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            total_amount=order.total_amount
        )

        return order_with_relations

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Order creation error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )

@router.get("/my", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    orders = (
        db.query(Order)
        .filter(Order.customer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific order"""
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .filter(Order.customer_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order

@router.get("/track/{order_number}")
async def track_order(
    order_number: str,
    db: Session = Depends(get_db)
):
    """Track order by order number (public endpoint)"""
    order = db.query(Order).filter(Order.order_number == order_number).first()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return {
        "order_number": order.order_number,
        "status": order.status,
        "estimated_ready_time": order.estimated_ready_time,
        "actual_ready_time": order.actual_ready_time,
        "created_at": order.created_at
    }

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an order (only if pending payment)"""
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .filter(Order.customer_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    if order.status != "pending_payment":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled at this stage"
        )

    order.status = "cancelled"
    db.commit()

    return {"message": "Order cancelled successfully"}

@router.post("/{order_id}/upload-payment-proof")
async def upload_payment_proof(
    order_id: int,
    proof_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload proof of payment for an order"""
    from ..models.database_models import BankTransfer

    # Verify order belongs to user
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .filter(Order.customer_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    try:
        # Check if payment proof already exists
        existing_transfer = db.query(BankTransfer).filter(BankTransfer.order_id == order_id).first()

        if existing_transfer:
            # Update existing record
            existing_transfer.reference_number = proof_data.get("reference_number", existing_transfer.reference_number)
            existing_transfer.amount = proof_data.get("amount", existing_transfer.amount)
            existing_transfer.sender_name = proof_data.get("sender_name", existing_transfer.sender_name)
            existing_transfer.sender_account = proof_data.get("sender_account", existing_transfer.sender_account)
            existing_transfer.receipt_image_url = proof_data.get("receipt_image_url", existing_transfer.receipt_image_url)
            existing_transfer.notes = proof_data.get("notes", existing_transfer.notes)
            existing_transfer.updated_at = datetime.now()
        else:
            # Create new bank transfer record
            bank_transfer = BankTransfer(
                order_id=order_id,
                reference_number=proof_data.get("reference_number", f"REF-{order.order_number}"),
                amount=proof_data.get("amount", order.total_amount),
                sender_name=proof_data.get("sender_name"),
                sender_account=proof_data.get("sender_account"),
                receipt_image_url=proof_data.get("receipt_image_url"),
                verification_status="pending",
                notes=proof_data.get("notes")
            )
            db.add(bank_transfer)

        # Update order payment status
        order.payment_status = "pending"
        order.updated_at = datetime.now()

        db.commit()

        # Send real-time notification to admin about payment proof upload
        from ..websockets import notify_admin_payment_uploaded
        await notify_admin_payment_uploaded(
            order_id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name
        )

        return {
            "message": "Payment proof uploaded successfully",
            "order_id": order_id,
            "status": "pending_verification"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload payment proof: {str(e)}"
        )

@router.get("/{order_id}/payment-proof")
async def get_payment_proof(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment proof for an order"""
    from ..models.database_models import BankTransfer

    # Verify order belongs to user
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .filter(Order.customer_id == current_user.id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Find the bank transfer record
    bank_transfer = db.query(BankTransfer).filter(BankTransfer.order_id == order_id).first()

    if not bank_transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payment proof found for this order"
        )

    return {
        "order_id": order_id,
        "reference_number": bank_transfer.reference_number,
        "amount": bank_transfer.amount,
        "sender_name": bank_transfer.sender_name,
        "receipt_image_url": bank_transfer.receipt_image_url,
        "verification_status": bank_transfer.verification_status,
        "created_at": bank_transfer.created_at.isoformat()
    }
