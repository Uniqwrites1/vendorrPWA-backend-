"""
Simple database initialization script
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import Base, User, MenuCategory, MenuItem, Order, OrderItem, UserRole, OrderStatus, PaymentStatus
from passlib.context import CryptContext

# Remove existing database
db_path = "vendorr.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    except PermissionError:
        print(f"Cannot remove {db_path} - it's being used by another process")
        print("Please stop the server first, then run this script again")
        sys.exit(1)

# Create new database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def init_database():
    """Initialize database with tables and sample data"""

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).first():
            print("Database already has data")
            return

        print("Adding sample data...")

        # Create admin user
        admin_user = User(
            email="admin@vendorr.com",
            phone="+1234567890",
            hashed_password=get_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)

        # Create test customer
        test_customer = User(
            email="customer@test.com",
            phone="+1234567893",
            hashed_password=get_password_hash("test123"),
            first_name="Test",
            last_name="Customer",
            role=UserRole.CUSTOMER,
            is_active=True,
            is_verified=True
        )
        db.add(test_customer)

        # Create menu categories
        burgers_cat = MenuCategory(
            name="Burgers",
            description="Delicious beef and chicken burgers",
            display_order=1,
            is_active=True
        )
        db.add(burgers_cat)

        sides_cat = MenuCategory(
            name="Sides",
            description="Crispy sides and appetizers",
            display_order=2,
            is_active=True
        )
        db.add(sides_cat)

        drinks_cat = MenuCategory(
            name="Beverages",
            description="Cold and hot drinks",
            display_order=3,
            is_active=True
        )
        db.add(drinks_cat)

        db.flush()  # Get category IDs

        # Create menu items
        burger1 = MenuItem(
            name="Classic Beef Burger",
            description="Juicy beef patty with lettuce, tomato, onion, and our special sauce",
            price=12.99,
            category_id=burgers_cat.id,
            is_available=True,
            is_featured=True,
            preparation_time=15,
            calories=650
        )
        db.add(burger1)

        fries = MenuItem(
            name="Crispy Fries",
            description="Golden crispy french fries with sea salt",
            price=4.99,
            category_id=sides_cat.id,
            is_available=True,
            preparation_time=8,
            calories=320
        )
        db.add(fries)

        drink1 = MenuItem(
            name="Fresh Lemonade",
            description="Freshly squeezed lemons with a hint of mint",
            price=3.99,
            category_id=drinks_cat.id,
            is_available=True,
            preparation_time=3,
            calories=120
        )
        db.add(drink1)

        db.flush()  # Get menu item IDs

        # Create sample order
        sample_order = Order(
            order_number="ORD-0001",
            customer_id=test_customer.id,
            status=OrderStatus.PREPARING,
            payment_status=PaymentStatus.CONFIRMED,
            subtotal=17.98,
            tax_amount=1.44,
            total_amount=19.42,
            customer_name="Test Customer",
            customer_phone="+1234567893",
            customer_email="customer@test.com",
            notes="Extra napkins please",
            payment_method="bank_transfer"
        )
        db.add(sample_order)
        db.flush()

        # Add order items
        order_item1 = OrderItem(
            order_id=sample_order.id,
            menu_item_id=burger1.id,
            quantity=1,
            unit_price=12.99,
            total_price=12.99
        )
        db.add(order_item1)

        order_item2 = OrderItem(
            order_id=sample_order.id,
            menu_item_id=fries.id,
            quantity=1,
            unit_price=4.99,
            total_price=4.99
        )
        db.add(order_item2)

        db.commit()
        print("Database initialized successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Done!")
