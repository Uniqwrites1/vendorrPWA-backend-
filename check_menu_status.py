"""
Check menu items and their status
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.models import MenuItem, MenuCategory

# Create SQLite database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_menu_status():
    db = SessionLocal()

    try:
        print("=== All Menu Items ===")
        items = db.query(MenuItem).all()
        for item in items:
            print(f"ID: {item.id}, Name: {item.name}, Status: {getattr(item, 'status', 'N/A')}, Available: {item.is_available}")

        print(f"\n=== Items with status='available' ===")
        available_items = db.query(MenuItem).filter(MenuItem.status == "available").all()
        print(f"Found {len(available_items)} items with status='available'")

        print(f"\n=== Items with is_available=True ===")
        available_items2 = db.query(MenuItem).filter(MenuItem.is_available == True).all()
        print(f"Found {len(available_items2)} items with is_available=True")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_menu_status()
