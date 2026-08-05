"""
database.py
-----------
Everything related to the database lives here.

If your professor asks "how do you connect to the database" or
"how are your tables structured" -- this is the file to open.
"""

import sqlite3

DB_NAME = "expenses.db"


def get_connection():
    """
    Opens a connection to the SQLite database file.
    SQLite has no separate server -- this just opens (or creates)
    a single file called expenses.db in the project folder.
    """
    return sqlite3.connect(DB_NAME)


def init_db():
    """
    Creates the categories and transactions tables if they don't
    already exist, and seeds a few default categories the first
    time the app is ever run.

    Called once, when the application starts (see main.py).
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            txn_type TEXT NOT NULL CHECK (txn_type IN ('Income', 'Expense')),
            amount REAL NOT NULL,
            txn_date TEXT NOT NULL,
            note TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    """)

    # Seed a few common categories the first time the app runs
    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        defaults = ["Food", "Travel", "Rent", "Shopping", "Salary", "Other"]
        cur.executemany("INSERT INTO categories (name) VALUES (?)", [(d,) for d in defaults])

    conn.commit()
    conn.close()
