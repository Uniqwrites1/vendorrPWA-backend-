"""
Check users table schema specifically
"""
import sqlite3

def check_users_schema():
    conn = sqlite3.connect('vendorr.db')
    cursor = conn.cursor()

    print("=== Users Table Schema ===")
    try:
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"Column: {col[1]} ({col[2]})")
    except Exception as e:
        print(f"Error checking users table: {e}")

    print("\n=== Sample User Data ===")
    try:
        cursor.execute("SELECT * FROM users LIMIT 2;")
        users = cursor.fetchall()
        for user in users:
            print(f"User: {user}")
    except Exception as e:
        print(f"Error getting user data: {e}")

    conn.close()

if __name__ == "__main__":
    check_users_schema()
