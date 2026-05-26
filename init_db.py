import sqlite3
import os

os.makedirs('instance', exist_ok=True)
db_path = os.path.join('instance', 'database.db')
schema_path = os.path.join('database', 'schema.sql')

print("Initializing database...")
with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = ON")
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
print("Database initialized successfully at", db_path)
