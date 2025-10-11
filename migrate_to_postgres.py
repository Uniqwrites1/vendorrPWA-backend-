"""
SQLite to PostgreSQL Migration Script for Vendorr PWA

This script migrates data from SQLite to PostgreSQL database.
Run this ONCE after setting up your PostgreSQL database.

Usage:
    python migrate_to_postgres.py

Prerequisites:
    - PostgreSQL database created and accessible
    - DATABASE_URL environment variable set to PostgreSQL connection string
    - Original SQLite database (vendorr.db) exists in the backend directory
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sqlite3
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_sqlite_to_postgres():
    """Migrate data from SQLite to PostgreSQL"""

    print("🚀 Starting SQLite to PostgreSQL Migration...\n")

    # Get PostgreSQL connection string
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("❌ Error: DATABASE_URL environment variable not set!")
        print("   Please set it to your PostgreSQL connection string:")
        print("   export DATABASE_URL='postgresql://user:password@host:port/database'")
        return False

    # Fix postgres:// to postgresql://
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)

    sqlite_path = "vendorr.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ Error: SQLite database not found at {sqlite_path}")
        return False

    print(f"✓ SQLite database found: {sqlite_path}")
    print(f"✓ PostgreSQL URL configured\n")

    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()

        # Connect to PostgreSQL
        pg_engine = create_engine(postgres_url)

        # Create all tables in PostgreSQL
        print("📋 Creating tables in PostgreSQL...")
        from app.models.database_models import Base
        Base.metadata.create_all(bind=pg_engine)
        print("✓ Tables created successfully\n")

        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=pg_engine)
        pg_session = SessionLocal()

        # Tables to migrate (in order due to foreign key constraints)
        tables = [
            "users",
            "menu_categories",
            "menu_items",
            "orders",
            "order_items",
            "bank_transfer_confirmations",
            "notifications",
            "reviews"
        ]

        total_migrated = 0

        for table in tables:
            print(f"📦 Migrating table: {table}")

            # Check if table exists in SQLite
            sqlite_cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            if not sqlite_cursor.fetchone():
                print(f"   ⚠️  Table {table} not found in SQLite, skipping...")
                continue

            # Get all rows from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()

            if not rows:
                print(f"   ℹ️  No data in {table}")
                continue

            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]

            migrated_count = 0
            for row in rows:
                # Convert row to dict
                row_dict = dict(zip(columns, row))

                # Build INSERT statement
                placeholders = ", ".join([f":{col}" for col in columns])
                insert_sql = f"""
                    INSERT INTO {table} ({", ".join(columns)})
                    VALUES ({placeholders})
                """

                try:
                    pg_session.execute(text(insert_sql), row_dict)
                    migrated_count += 1
                except Exception as e:
                    print(f"   ⚠️  Error inserting row: {e}")
                    continue

            pg_session.commit()
            total_migrated += migrated_count
            print(f"   ✓ Migrated {migrated_count} rows from {table}\n")

        # Close connections
        sqlite_conn.close()
        pg_session.close()

        print(f"\n✅ Migration completed successfully!")
        print(f"📊 Total rows migrated: {total_migrated}")
        print(f"\n🎉 Your PostgreSQL database is ready to use!")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Vendorr PWA - Database Migration Tool")
    print("  SQLite → PostgreSQL")
    print("=" * 60)
    print()

    confirm = input("⚠️  This will copy all data to PostgreSQL. Continue? (yes/no): ")
    if confirm.lower() != "yes":
        print("Migration cancelled.")
        sys.exit(0)

    print()
    success = migrate_sqlite_to_postgres()

    if success:
        print("\n💡 Next steps:")
        print("   1. Test your application with PostgreSQL")
        print("   2. Verify all data migrated correctly")
        print("   3. Deploy to production!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
