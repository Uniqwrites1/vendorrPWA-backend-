from app.core.database import SessionLocal
from app.models.database_models import MenuItem

db = SessionLocal()

# Check menu items
items = db.query(MenuItem).all()
print(f'\n✅ Total menu items: {len(items)}')

if items:
    print('\n📋 First 5 items:')
    for item in items[:5]:
        print(f'  - {item.name}')
        print(f'    Category ID: {item.category_id}')
        print(f'    Price: ₦{item.price}')
        print(f'    Featured: {item.is_featured}')
        print(f'    Available: {item.is_available}')
        print()
    
    # Check featured items
    featured = db.query(MenuItem).filter(MenuItem.is_featured == True, MenuItem.is_available == True).all()
    print(f'⭐ Featured & Available items: {len(featured)}')
    for item in featured:
        print(f'  - {item.name}')
else:
    print('\n❌ No menu items found in database!')

db.close()
