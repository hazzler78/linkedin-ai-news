import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_file = 'users.db'
        self.init_db()

    def init_db(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_user(self, name: str, email: str) -> bool:
        """Add a new user to the database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO users (name, email) VALUES (?, ?)',
                    (name, email)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # Email already exists
            return False

    def get_user_by_email(self, email: str) -> dict:
        """Get user information by email."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, name, email, created_at FROM users WHERE email = ?',
                (email,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2],
                    'created_at': result[3]
                }
            return None

    def user_exists(self, email: str) -> bool:
        """Check if a user exists by email."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM users WHERE email = ?', (email,))
            return cursor.fetchone() is not None 