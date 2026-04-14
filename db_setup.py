import sqlite3
import os
import hashlib

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
        ("Alice Smith", "alice@example.com", hashlib.sha256("password123".encode()).hexdigest(), "VIP Customer"),
        ("Bob Jones", "bob@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Frequent returns"),
        ("Charlie Brown", "charlie@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Regular"),
        ("Diana Prince", "diana@example.com", hashlib.sha256("password123".encode()).hexdigest(), "High value cart limit"),
        ("Eve Adams", "eve@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Loyalty program"),
        ("Frank Castle", "frank@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Watchlist"),
        ("Grace Hopper", "grace@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Tech Lead"),
        ("Henry Ford", "henry@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Bulk ordering"),
        ("Ivy Carter", "ivy@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Standard"),
        ("Jack Sparrow", "jack@example.com", hashlib.sha256("password123".encode()).hexdigest(), "Flagged for fraud")
    ]
    c.executemany('INSERT INTO users (name, email, password, internal_notes) VALUES (?, ?, ?, ?)', users)
    
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