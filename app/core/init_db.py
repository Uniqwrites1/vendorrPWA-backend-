"""
Database initialization and seed data for Vendorr PWA
"""
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..models.database_models import *
from ..core.database import engine, SessionLocal
import json

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def seed_database():
    """Seed the database with initial data"""
    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already seeded")
            return

        # Create admin user
        admin_user = User(
            email="admin@vendorr.com",
            phone="+1234567890",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role="admin",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)

        # Create staff users
        kitchen_staff = User(
            email="kitchen@vendorr.com",
            phone="+1234567891",
            hashed_password=get_password_hash("kitchen123"),
            first_name="Kitchen",
            last_name="Staff",
            role="kitchen",
            is_active=True,
            is_verified=True
        )
        db.add(kitchen_staff)

        counter_staff = User(
            email="counter@vendorr.com",
            phone="+1234567892",
            hashed_password=get_password_hash("counter123"),
            first_name="Counter",
            last_name="Staff",
            role="counter",
            is_active=True,
            is_verified=True
        )
        db.add(counter_staff)

        # Create test customer
        test_customer = User(
            email="customer@test.com",
            phone="+1234567893",
            hashed_password=get_password_hash("test123"),
            first_name="Test",
            last_name="Customer",
            role="customer",
            is_active=True,
            is_verified=True
        )
        db.add(test_customer)

        # Create menu categories
        categories_data = [
            {"name": "Burgers", "description": "Delicious beef and chicken burgers", "sort_order": 1},
            {"name": "Wraps", "description": "Fresh wraps with various fillings", "sort_order": 2},
            {"name": "Sides", "description": "Crispy sides and appetizers", "sort_order": 3},
            {"name": "Beverages", "description": "Cold and hot drinks", "sort_order": 4},
            {"name": "Desserts", "description": "Sweet treats and desserts", "sort_order": 5}
        ]

        categories = []
        for cat_data in categories_data:
            category = MenuCategory(**cat_data)
            db.add(category)
            categories.append(category)

        db.flush()  # Get the IDs

        # Create menu items
        menu_items_data = [
            # Burgers
            {
                "name": "Classic Beef Burger",
                "description": "Juicy beef patty with lettuce, tomato, onion, and our special sauce",
                "price": 12.99,
                "category_id": categories[0].id,
                "is_featured": True,
                "preparation_time": 15,
                "calories": 650,
                "allergens": json.dumps(["gluten", "dairy"]),
                "customization_options": json.dumps([
                    {"name": "Extra Cheese", "price": 1.50},
                    {"name": "Bacon", "price": 2.00},
                    {"name": "Avocado", "price": 1.75}
                ])
            },
            {
                "name": "Chicken Deluxe",
                "description": "Grilled chicken breast with crispy lettuce and mayo",
                "price": 11.99,
                "category_id": categories[0].id,
                "preparation_time": 12,
                "calories": 520,
                "allergens": json.dumps(["gluten", "dairy"]),
                "customization_options": json.dumps([
                    {"name": "Spicy Sauce", "price": 0.50},
                    {"name": "Extra Chicken", "price": 3.00}
                ])
            },
            # Wraps
            {
                "name": "Mediterranean Wrap",
                "description": "Grilled chicken, hummus, vegetables, and tzatziki in a soft tortilla",
                "price": 10.99,
                "category_id": categories[1].id,
                "is_featured": True,
                "preparation_time": 10,
                "calories": 480,
                "allergens": json.dumps(["gluten", "dairy"]),
                "customization_options": json.dumps([
                    {"name": "Extra Hummus", "price": 1.00},
                    {"name": "Feta Cheese", "price": 1.50}
                ])
            },
            {
                "name": "BBQ Chicken Wrap",
                "description": "Tender BBQ chicken with coleslaw and crispy onions",
                "price": 11.49,
                "category_id": categories[1].id,
                "preparation_time": 10,
                "calories": 510,
                "allergens": json.dumps(["gluten", "dairy"]),
                "customization_options": json.dumps([
                    {"name": "Extra BBQ Sauce", "price": 0.50},
                    {"name": "Jalapeños", "price": 0.75}
                ])
            },
            # Sides
            {
                "name": "Crispy Fries",
                "description": "Golden crispy french fries with sea salt",
                "price": 4.99,
                "category_id": categories[2].id,
                "preparation_time": 8,
                "calories": 320,
                "allergens": json.dumps([]),
                "customization_options": json.dumps([
                    {"name": "Cheese Sauce", "price": 1.50},
                    {"name": "Truffle Oil", "price": 2.00}
                ])
            },
            {
                "name": "Loaded Nachos",
                "description": "Crispy nachos with cheese, jalapeños, and sour cream",
                "price": 8.99,
                "category_id": categories[2].id,
                "preparation_time": 12,
                "calories": 580,
                "allergens": json.dumps(["dairy"]),
                "customization_options": json.dumps([
                    {"name": "Guacamole", "price": 2.00},
                    {"name": "Extra Cheese", "price": 1.50}
                ])
            },
            # Beverages
            {
                "name": "Fresh Lemonade",
                "description": "Freshly squeezed lemons with a hint of mint",
                "price": 3.99,
                "category_id": categories[3].id,
                "preparation_time": 3,
                "calories": 120,
                "allergens": json.dumps([]),
                "customization_options": json.dumps([
                    {"name": "Extra Mint", "price": 0.25},
                    {"name": "Sugar-Free", "price": 0.00}
                ])
            },
            {
                "name": "Craft Cola",
                "description": "House-made cola with natural ingredients",
                "price": 2.99,
                "category_id": categories[3].id,
                "preparation_time": 2,
                "calories": 150,
                "allergens": json.dumps([]),
                "customization_options": json.dumps([])
            },
            # Desserts
            {
                "name": "Chocolate Brownie",
                "description": "Rich chocolate brownie with vanilla ice cream",
                "price": 6.99,
                "category_id": categories[4].id,
                "preparation_time": 5,
                "calories": 420,
                "allergens": json.dumps(["gluten", "dairy", "eggs"]),
                "customization_options": json.dumps([
                    {"name": "Extra Ice Cream", "price": 1.50},
                    {"name": "Nuts", "price": 1.00}
                ])
            }
        ]

        for item_data in menu_items_data:
            menu_item = MenuItem(**item_data)
            db.add(menu_item)

        # Create sample orders
        db.flush()  # Get menu item IDs

        sample_order = Order(
            order_number="ORD-001",
            customer_id=test_customer.id,
            status=OrderStatus.PREPARING,
            payment_status=PaymentStatus.COMPLETED,
            total_amount=25.97,
            tax_amount=2.08,
            customer_name="Test Customer",
            customer_phone="+1234567893",
            customer_email="customer@test.com",
            notes="Extra napkins please",
            payment_method="bank_transfer"
        )
        db.add(sample_order)
        db.flush()

        # Add order items
        burger_item = db.query(MenuItem).filter(MenuItem.name == "Classic Beef Burger").first()
        fries_item = db.query(MenuItem).filter(MenuItem.name == "Crispy Fries").first()

        order_item1 = OrderItem(
            order_id=sample_order.id,
            menu_item_id=burger_item.id,
            quantity=1,
            unit_price=burger_item.price,
            total_price=burger_item.price,
            customizations=json.dumps([{"name": "Extra Cheese", "price": 1.50}])
        )

        order_item2 = OrderItem(
            order_id=sample_order.id,
            menu_item_id=fries_item.id,
            quantity=2,
            unit_price=fries_item.price,
            total_price=fries_item.price * 2
        )

        db.add(order_item1)
        db.add(order_item2)

        # Create sample notifications
        notification = Notification(
            user_id=test_customer.id,
            order_id=sample_order.id,
            title="Order Update",
            message="Your order #ORD-001 is being prepared!",
            type="order_status"
        )
        db.add(notification)

        # Commit all changes
        db.commit()
        print("Database seeded successfully!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed_database()
