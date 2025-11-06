
#!/usr/bin/env python3
"""
Initialize UPAK database with all required tables
"""

import sqlite3
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:////tmp/upak_test/upak_test.db')

def init_database():
    """Initialize database with all required tables"""
    db_path = DATABASE_URL.replace('sqlite:///', '')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Initializing database at: {db_path}")
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_type TEXT DEFAULT 'free',
            subscription_expires DATETIME,
            cards_limit INTEGER DEFAULT 0,
            cards_used INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ Created users table")
    
    # Create payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            status TEXT DEFAULT 'pending',
            package TEXT,
            confirmation_url TEXT,
            payment_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✓ Created payments table")
    
    # Create cards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            pdf_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✓ Created cards table")
    
    # Create orders table (for backward compatibility)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            amount DECIMAL(10,2),
            status TEXT DEFAULT 'pending',
            payment_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_pro_package BOOLEAN DEFAULT 0,
            remaining_cards INTEGER,
            expires_at DATETIME,
            pack_qty INTEGER DEFAULT 1,
            package TEXT DEFAULT 'start'
        )
    ''')
    print("✓ Created orders table")
    
    # Create pro_subscriptions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pro_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            remaining_cards INTEGER DEFAULT 10,
            expires_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✓ Created pro_subscriptions table")
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cards_user_id ON cards(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pro_subs_user_id ON pro_subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pro_subs_active ON pro_subscriptions(is_active)')
    print("✓ Created indexes")
    
    conn.commit()
    conn.close()
    
    print("✓ Database initialization completed successfully!")

if __name__ == '__main__':
    init_database()
