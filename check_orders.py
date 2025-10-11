#!/usr/bin/env python3
"""Script to check orders in the database"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_db
from app.models import Order, OrderItem, MenuItem, User
from sqlalchemy.orm import joinedload

def check_orders():
    db = next(get_db())

    print("=== Checking Orders in Database ===")

    # Get all orders
    orders = db.query(Order).options(
        joinedload(Order.customer),
        joinedload(Order.order_items).joinedload(OrderItem.menu_item)
    ).all()

    print(f"Total orders found: {len(orders)}")

    for order in orders:
        print(f"\nOrder ID: {order.id}")
        print(f"Order Number: {order.order_number}")
        print(f"Customer: {order.customer.email if order.customer else order.customer_email or 'Unknown'}")
        print(f"Status: {order.status}")
        print(f"Total: ${order.total_amount}")
        print(f"Created: {order.created_at}")
        print(f"Items: {len(order.order_items)}")

        for item in order.order_items:
            print(f"  - {item.menu_item.name}: {item.quantity}x ${item.unit_price}")

    print("\n=== Checking Menu Items ===")
    menu_items = db.query(MenuItem).all()
    print(f"Total menu items: {len(menu_items)}")

    print("\n=== Checking Users ===")
    users = db.query(User).all()
    print(f"Total users: {len(users)}")

    db.close()

if __name__ == "__main__":
    check_orders()
