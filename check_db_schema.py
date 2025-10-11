import sqlite3

conn = sqlite3.connect('vendorr.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    cursor.execute(f'PRAGMA table_info({table_name})')
    print(f'\n=== {table_name} ===')
    for row in cursor.fetchall():
        print(f'  {row[1]} ({row[2]})')

conn.close()
