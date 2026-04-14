import sqlite3
import os
import hashlib
import secrets

DB_PATH = 'shopeasy.db'

def setup_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create tables
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            salt TEXT NOT NULL,
            internal_notes TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            card_last4 TEXT NOT NULL,
            total REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Populate Users (10 users)
    users = [
        ("Alice Smith", "alice@example.com", "password123"),
        ("Bob Jones", "bob@example.com", "password123"),
        ("Charlie Brown", "charlie@example.com", "password123"),
        ("Diana Prince", "diana@example.com", "password123"),
        ("Eve Adams", "eve@example.com", "password123"),
        ("Frank Castle", "frank@example.com", "password123"),
        ("Grace Hopper", "grace@example.com", "password123"),
        ("Henry Ford", "henry@example.com", "password123"),
        ("Ivy Carter", "ivy@example.com", "password123"),
        ("Jack Sparrow", "jack@example.com", "password123")
    ]
    
    hashed_users = []
    for user in users:
        salt = secrets.token_hex(16)
        password = user[2]
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        hashed_password = hashed_password.hex()
        hashed_users.append((user[0], user[1], hashed_password, salt, "VIP Customer" if user[0] == 'Alice Smith' else 'Regular'))
    
    c.executemany('INSERT INTO users (name, email, password, salt, internal_notes) VALUES (?, ?, ?, ?, ?)', hashed_users)
    
    # Populate Products (5 products)
    products = [
        ("Wireless Noise-Canceling Headphones", "Premium sound with 30-hour battery life", 299.99, "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"),
        ("Smart Watch Series 8", "Track your health and fitness effortlessly", 399.99, "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&auto=format&fit=crop&q=60"),
        ("4K Ultra HD Smart TV", "55-inch display with vibrant colors", 499.99, "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=500&auto=format&fit=crop&q=60"),
        ("Mechanical Gaming Keyboard", "RGB backlit with tactile switches", 129.99, "https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&auto=format&fit=crop&q=60"),
        ("Ultra-Light Laptop", "16GB RAM, 512GB SSD, all-day battery", 1199.99, "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60")
    ]
    c.executemany('INSERT INTO products (name, description, price, image_url) VALUES (?, ?, ?, ?)', products)
    
    # Populate Orders
    orders = [
        (1, "Alice Smith", "alice@example.com", "123 Elm St, NY", "4242", 299.99),
        (2, "Bob Jones", "bob@example.com", "456 Oak Ave, CA", "1111", 399.99),
        (3, "Charlie Brown", "charlie@example.com", "789 Pine Rd, TX", "9999", 129.99),
        (1, "Alice Smith", "alice@example.com", "123 Elm St, NY", "4242", 1199.99),
        (5, "Eve Adams", "eve@example.com", "321 Cedar Ln, WA", "8888", 499.99)
    ]
    c.executemany('INSERT INTO orders (user_id, name, email, address, card_last4, total) VALUES (?, ?, ?, ?, ?, ?)', orders)
    
    conn.commit()
    
    conn.close()
    print("Database initialised successfully.")

if __name__ == '__main__':
    setup_db()