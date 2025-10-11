"""
Add menu items to existing database
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.models import Base, MenuCategory, MenuItem

# Create SQLite database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def add_menu_items():
    """Add menu categories and items to the database"""
    db = SessionLocal()

    try:
        # Check if menu items already exist
        existing_items = db.query(MenuItem).count()
        if existing_items > 0:
            print(f"Database already has {existing_items} menu items")
            return

        print("Adding menu categories and items...")

        # Create menu categories
        burgers_cat = MenuCategory(
            name="Burgers",
            description="Delicious beef and chicken burgers",
            display_order=1,
            is_active=True
        )
        db.add(burgers_cat)

        wraps_cat = MenuCategory(
            name="Wraps",
            description="Fresh wraps with various fillings",
            display_order=2,
            is_active=True
        )
        db.add(wraps_cat)

        sides_cat = MenuCategory(
            name="Sides",
            description="Crispy sides and appetizers",
            display_order=3,
            is_active=True
        )
        db.add(sides_cat)

        drinks_cat = MenuCategory(
            name="Beverages",
            description="Cold and hot drinks",
            display_order=4,
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
            calories=650,
            customization_options=json.dumps([
                {"name": "Extra Cheese", "price": 1.50},
                {"name": "Bacon", "price": 2.00},
                {"name": "Avocado", "price": 1.75}
            ])
        )
        db.add(burger1)

        burger2 = MenuItem(
            name="Chicken Deluxe Burger",
            description="Grilled chicken breast with avocado, lettuce, and mayo",
            price=11.99,
            category_id=burgers_cat.id,
            is_available=True,
            preparation_time=12,
            calories=580
        )
        db.add(burger2)

        wrap1 = MenuItem(
            name="Mediterranean Wrap",
            description="Grilled chicken, hummus, vegetables, and tzatziki in a soft tortilla",
            price=10.99,
            category_id=wraps_cat.id,
            is_available=True,
            is_featured=True,
            preparation_time=10,
            calories=480
        )
        db.add(wrap1)

        wrap2 = MenuItem(
            name="Caesar Chicken Wrap",
            description="Crispy chicken with Caesar dressing, parmesan, and romaine lettuce",
            price=9.99,
            category_id=wraps_cat.id,
            is_available=True,
            preparation_time=8,
            calories=520
        )
        db.add(wrap2)

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

        nachos = MenuItem(
            name="Loaded Nachos",
            description="Tortilla chips with cheese, jalapeños, and sour cream",
            price=7.99,
            category_id=sides_cat.id,
            is_available=True,
            preparation_time=10,
            calories=450
        )
        db.add(nachos)

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

        drink2 = MenuItem(
            name="Iced Coffee",
            description="Cold brew coffee served over ice",
            price=4.49,
            category_id=drinks_cat.id,
            is_available=True,
            preparation_time=2,
            calories=45
        )
        db.add(drink2)

        db.commit()
        print("Menu items added successfully!")

    except Exception as e:
        print(f"Error adding menu items: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_menu_items()
