"""
Fix menu items to have proper values for API schema
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app.models import MenuItem

# Create SQLite database
DATABASE_URL = "sqlite:///./vendorr.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_menu_items():
    """Fix menu items to have proper values"""
    db = SessionLocal()

    try:
        # Get all menu items
        items = db.query(MenuItem).all()

        print(f"Fixing {len(items)} menu items...")

        for i, item in enumerate(items):
            # Set default values for missing fields
            if item.spice_level is None:
                item.spice_level = 1  # Default mild spice level

            # Add popularity_score and total_orders as attributes (for schema compatibility)
            # These will be computed or set to defaults

            print(f"Fixed item {i+1}: {item.name}")

        db.commit()
        print("Menu items fixed successfully!")

    except Exception as e:
        print(f"Error fixing menu items: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_menu_items()
