"""
Quick diagnostic to check menu item status values in production database
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    print("Please set it manually or run from Railway environment")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Query all menu items with their status
    query = text("""
        SELECT
            id,
            name,
            status,
            is_available,
            category_id,
            price
        FROM menu_items
        ORDER BY id
        LIMIT 20
    """)

    result = db.execute(query)
    rows = result.fetchall()

    print(f"\n{'='*80}")
    print(f"MENU ITEMS STATUS CHECK - Total items found: {len(rows)}")
    print(f"{'='*80}\n")

    if len(rows) == 0:
        print("⚠️  NO MENU ITEMS FOUND IN DATABASE!")
    else:
        print(f"{'ID':<5} {'Name':<30} {'Status':<15} {'Available':<10} {'Price':<10}")
        print(f"{'-'*80}")

        null_count = 0
        available_count = 0
        other_count = 0

        for row in rows:
            item_id, name, status, is_available, category_id, price = row
            status_display = status if status else "NULL"

            if status is None:
                null_count += 1
                status_display = "❌ NULL"
            elif status == "available":
                available_count += 1
                status_display = "✅ available"
            else:
                other_count += 1
                status_display = f"⚠️  {status}"

            print(f"{item_id:<5} {name[:28]:<30} {status_display:<20} {str(is_available):<10} ₦{price:<10.2f}")

        print(f"\n{'='*80}")
        print(f"SUMMARY:")
        print(f"  NULL status: {null_count}")
        print(f"  'available' status: {available_count}")
        print(f"  Other status: {other_count}")
        print(f"{'='*80}\n")

        if null_count > 0:
            print("🚨 ACTION REQUIRED: Run this SQL in Supabase:")
            print("   UPDATE menu_items SET status = 'available' WHERE status IS NULL;")
        elif available_count > 0:
            print("✅ Menu items have proper status! API should work.")
            print("   If API still returns empty, check:")
            print("   1. Railway deployment completed")
            print("   2. Database connection is correct")
            print("   3. Check Railway logs for errors")

finally:
    db.close()
