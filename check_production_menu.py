"""
Check menu items status in production database via Railway backend
This connects to the same database as the production backend
"""
import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load production environment variables
load_dotenv('.env.production')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env.production")
    sys.exit(1)

print(f"🔗 Connecting to database...")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check menu items count and status
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_items,
                COUNT(CASE WHEN status = 'available' THEN 1 END) as available_status,
                COUNT(CASE WHEN status IS NULL THEN 1 END) as null_status,
                COUNT(CASE WHEN is_available = true THEN 1 END) as is_available_true
            FROM menu_items
        """))

        row = result.fetchone()
        print(f"\n📊 Database Statistics:")
        print(f"  Total items: {row[0]}")
        print(f"  Items with status='available': {row[1]}")
        print(f"  Items with status=NULL: {row[2]}")
        print(f"  Items with is_available=true: {row[3]}")

        # Show sample items
        result = conn.execute(text("""
            SELECT id, name, status, is_available
            FROM menu_items
            LIMIT 5
        """))

        print(f"\n📋 Sample Items:")
        for row in result:
            print(f"  ID: {row[0]}, Name: {row[1]}, Status: {row[2]}, Available: {row[3]}")

        print("\n✅ Check complete!")

except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    engine.dispose()
