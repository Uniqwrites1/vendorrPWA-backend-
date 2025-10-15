"""
Update local database with Nigerian Naira menu items
This will replace the old dollar-priced items with new Naira-priced items
"""
from app.core.database import SessionLocal
from app.models.database_models import MenuItem, Category

db = SessionLocal()

try:
    print("🗑️  Deleting old menu items...")
    db.query(MenuItem).delete()

    print("🗑️  Deleting old categories...")
    db.query(Category).delete()

    db.commit()

    print("\n📦 Creating new categories...")
    categories_data = [
        {"id": 1, "name": "Noodles", "description": "Delicious noodle dishes", "display_order": 1, "is_active": True},
        {"id": 2, "name": "Pasta", "description": "Italian-style pasta dishes", "display_order": 2, "is_active": True},
        {"id": 3, "name": "Meats", "description": "Grilled and fried meat options", "display_order": 3, "is_active": True},
        {"id": 4, "name": "Drinks", "description": "Refreshing beverages", "display_order": 4, "is_active": True},
        {"id": 5, "name": "Desserts", "description": "Sweet treats", "display_order": 5, "is_active": True},
    ]

    for cat_data in categories_data:
        category = Category(**cat_data)
        db.add(category)

    db.commit()
    print(f"✅ Created {len(categories_data)} categories")

    print("\n🍜 Creating menu items with Naira prices...")
    menu_items_data = [
        # Noodles
        {"name": "Chicken Stir-Fry Noodles", "description": "Stir-fried noodles with grilled chicken and vegetables",
         "price": 2500, "category_id": 1, "is_available": True, "is_featured": True, "preparation_time": 20},
        {"name": "Seafood Noodles", "description": "Spicy noodles with prawns, squid, and fish chunks",
         "price": 2800, "category_id": 1, "is_available": True, "is_featured": False, "preparation_time": 25},
        {"name": "Vegetable Noodles", "description": "Savory noodles mixed with fresh veggies and soy sauce",
         "price": 2000, "category_id": 1, "is_available": True, "is_featured": False, "preparation_time": 15},

        # Pasta
        {"name": "Spaghetti Bolognese", "description": "Classic pasta with minced beef and tomato sauce",
         "price": 3000, "category_id": 2, "is_available": True, "is_featured": True, "preparation_time": 25},
        {"name": "Jollof Spaghetti", "description": "Nigerian-style pasta cooked in rich jollof sauce",
         "price": 2700, "category_id": 2, "is_available": True, "is_featured": True, "preparation_time": 20},
        {"name": "Creamy Alfredo Pasta", "description": "Pasta in creamy white sauce with chicken strips",
         "price": 3200, "category_id": 2, "is_available": True, "is_featured": False, "preparation_time": 25},

        # Meats
        {"name": "Grilled Chicken", "description": "Tender grilled chicken marinated with special herbs",
         "price": 2500, "category_id": 3, "is_available": True, "is_featured": True, "preparation_time": 30},
        {"name": "Beef Suya", "description": "Spicy Nigerian-style grilled beef skewers",
         "price": 2200, "category_id": 3, "is_available": True, "is_featured": True, "preparation_time": 25},
        {"name": "Barbecue Ribs", "description": "Juicy pork ribs in smoky BBQ sauce",
         "price": 3500, "category_id": 3, "is_available": True, "is_featured": False, "preparation_time": 35},
        {"name": "Peppered Meat", "description": "Spicy fried beef chunks tossed in rich pepper sauce",
         "price": 2300, "category_id": 3, "is_available": True, "is_featured": False, "preparation_time": 20},
        {"name": "Peppered Pomo", "description": "Soft cow skin cooked in savory spicy pepper mix",
         "price": 1800, "category_id": 3, "is_available": True, "is_featured": False, "preparation_time": 25},

        # Drinks
        {"name": "Chapman", "description": "Refreshing Nigerian mocktail with citrus and bitters",
         "price": 1200, "category_id": 4, "is_available": True, "is_featured": False, "preparation_time": 5},
        {"name": "Zobo Drink", "description": "Hibiscus-based drink with ginger and pineapple flavor",
         "price": 1000, "category_id": 4, "is_available": True, "is_featured": False, "preparation_time": 5},
        {"name": "Fresh Fruit Juice", "description": "Blend of orange, pineapple, and watermelon juice",
         "price": 1500, "category_id": 4, "is_available": True, "is_featured": False, "preparation_time": 5},

        # Desserts
        {"name": "Chocolate Cake", "description": "Rich moist chocolate cake slice",
         "price": 1800, "category_id": 5, "is_available": True, "is_featured": False, "preparation_time": 5},
        {"name": "Vanilla Ice Cream", "description": "Creamy vanilla ice cream topped with syrup",
         "price": 1500, "category_id": 5, "is_available": True, "is_featured": False, "preparation_time": 5},
        {"name": "Fruit Parfait", "description": "Layered dessert with yogurt, granola, and fresh fruits",
         "price": 2000, "category_id": 5, "is_available": True, "is_featured": False, "preparation_time": 10},
    ]

    for item_data in menu_items_data:
        item = MenuItem(**item_data)
        db.add(item)

    db.commit()
    print(f"✅ Created {len(menu_items_data)} menu items")

    # Verify
    print("\n📊 Database Summary:")
    print(f"  Categories: {db.query(Category).count()}")
    print(f"  Menu Items: {db.query(MenuItem).count()}")
    print(f"  Featured Items: {db.query(MenuItem).filter(MenuItem.is_featured == True).count()}")

    print("\n💰 Sample Prices:")
    items = db.query(MenuItem).limit(5).all()
    for item in items:
        print(f"  {item.name}: ₦{item.price:,.2f}")

    print("\n✅ Local database updated successfully with Naira prices!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.rollback()
finally:
    db.close()
