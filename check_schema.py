"""
Check database schema
"""
import sqlite3

def check_schema():
    conn = sqlite3.connect('vendorr.db')
    cursor = conn.cursor()

    print("=== Database Tables ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"Table: {table[0]}")

    print("\n=== Menu Categories Table Schema ===")
    try:
        cursor.execute("PRAGMA table_info(menu_categories);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error checking menu_categories: {e}")

    print("\n=== Menu Items Table Schema ===")
    try:
        cursor.execute("PRAGMA table_info(menu_items);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error checking menu_items: {e}")

    conn.close()

if __name__ == "__main__":
    check_schema()
