"""
SQLite database implementation for CartUp agent
Replaces the in-memory DUMMY_DB with persistent storage
"""

import sqlite3
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from pathlib import Path

# Database path
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "cartup.db"


@contextmanager
def get_connection():
    """Context manager for database connections with transaction support."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _create_schema(conn: sqlite3.Connection):
    """Create database schema if tables don't exist."""
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            created_at TEXT
        )
    """)
    
    # Products table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            in_stock INTEGER DEFAULT 1,
            stock_quantity INTEGER DEFAULT 0
        )
    """)
    
    # Orders table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            status TEXT NOT NULL,
            amount REAL NOT NULL,
            delivery_date TEXT,
            address TEXT,
            created_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Order items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)
    
    # Tickets table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            issue TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)
    
    # Returns table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            order_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            refund_status TEXT NOT NULL,
            reason TEXT,
            created_at TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    """)
    
    # Recommendations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Wishlists table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wishlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            UNIQUE(user_id, product_id)
        )
    """)
    
    # ID sequences table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS id_sequences (
            entity_type TEXT PRIMARY KEY,
            next_value INTEGER NOT NULL DEFAULT 0
        )
    """)


def _next_id(entity_type: str) -> str:
    """Generate next ID for an entity type using SQLite id_sequences table."""
    prefix_map = {
        "ticket": "t",
        "order": "o",
        "product": "p",
        "user": "u",
    }
    prefix = prefix_map.get(entity_type, "x")
    
    with get_connection() as conn:
        # Get or create sequence entry
        cursor = conn.execute(
            "SELECT next_value FROM id_sequences WHERE entity_type = ?",
            (entity_type,)
        )
        row = cursor.fetchone()
        
        if row is None:
            # Initialize sequence
            conn.execute(
                "INSERT INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
                (entity_type, 1)
            )
            counter = 1
        else:
            # Increment and update
            counter = row["next_value"] + 1
            conn.execute(
                "UPDATE id_sequences SET next_value = ? WHERE entity_type = ?",
                (counter, entity_type)
            )
    
    return f"{prefix}{counter}"


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Get user's orders
            order_cursor = conn.execute(
                "SELECT order_id FROM orders WHERE user_id = ? ORDER BY created_at",
                (user_id,)
            )
            order_ids = [r["order_id"] for r in order_cursor.fetchall()]
            
            return {
                "user_id": row["user_id"],
                "name": row["name"],
                "phone": row["phone"],
                "email": row["email"],
                "orders": order_ids,
            }
    except Exception:
        return None


def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Get order by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM orders WHERE order_id = ?",
                (order_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            # Get order items
            items_cursor = conn.execute(
                "SELECT product_name FROM order_items WHERE order_id = ?",
                (order_id,)
            )
            items = [r["product_name"] for r in items_cursor.fetchall()]
            
            return {
                "order_id": row["order_id"],
                "user_id": row["user_id"],
                "status": row["status"],
                "items": items,
                "amount": row["amount"],
                "delivery_date": row["delivery_date"],
                "address": row["address"],
                "created_at": row["created_at"],
            }
    except Exception:
        return None


def get_product(product_id: str) -> Optional[Dict[str, Any]]:
    """Get product by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM products WHERE product_id = ?",
                (product_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "product_id": row["product_id"],
                "name": row["name"],
                "description": row["description"],
                "price": row["price"],
                "category": row["category"],
                "in_stock": bool(row["in_stock"]),
                "stock_quantity": row["stock_quantity"],
            }
    except Exception:
        return None


def get_ticket(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Get ticket by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM tickets WHERE ticket_id = ?",
                (ticket_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "ticket_id": row["ticket_id"],
                "order_id": row["order_id"],
                "issue": row["issue"],
                "status": row["status"],
                "created_at": row["created_at"],
            }
    except Exception:
        return None


def get_return(order_id: str) -> Optional[Dict[str, Any]]:
    """Get return by order ID."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM returns WHERE order_id = ?",
                (order_id,)
            )
            row = cursor.fetchone()
            
            if row is None:
                return None
            
            return {
                "order_id": row["order_id"],
                "status": row["status"],
                "refund_status": row["refund_status"],
                "reason": row["reason"],
                "created_at": row["created_at"],
            }
    except Exception:
        return None


# Write helper functions

def update_order_address(order_id: str, address: str) -> bool:
    """Update delivery address for an order."""
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE orders SET address = ? WHERE order_id = ?",
                (address, order_id)
            )
            return conn.total_changes > 0
    except Exception:
        return False


def create_ticket_record(ticket_id: str, order_id: str, issue: str, status: str = "Open", created_at: str = None) -> bool:
    """Create a ticket record."""
    try:
        if created_at is None:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d")
        
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO tickets (ticket_id, order_id, issue, status, created_at) VALUES (?, ?, ?, ?, ?)",
                (ticket_id, order_id, issue, status, created_at)
            )
            return True
    except Exception:
        return False


def create_return_record(order_id: str, reason: str, status: str = "Pending Courier Pickup", 
                         refund_status: str = "Not Initiated", created_at: str = None) -> bool:
    """Create a return record."""
    try:
        if created_at is None:
            from datetime import datetime
            created_at = datetime.now().strftime("%Y-%m-%d")
        
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO returns (order_id, status, refund_status, reason, created_at) VALUES (?, ?, ?, ?, ?)",
                (order_id, status, refund_status, reason, created_at)
            )
            return True
    except Exception:
        return False


def update_refund_status(order_id: str, status: str) -> bool:
    """Update refund status for a return."""
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE returns SET refund_status = ? WHERE order_id = ?",
                (status, order_id)
            )
            return conn.total_changes > 0
    except Exception:
        return False


def add_to_wishlist(user_id: str, product_id: str) -> bool:
    """Add a product to user's wishlist."""
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO wishlists (user_id, product_id) VALUES (?, ?)",
                (user_id, product_id)
            )
            return True
    except Exception:
        return False


def get_recommendations_for_user(user_id: str) -> List[str]:
    """Get list of recommended product names for a user."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT product_name FROM recommendations WHERE user_id = ?",
                (user_id,)
            )
            return [r["product_name"] for r in cursor.fetchall()]
    except Exception:
        return []


def get_wishlist_for_user(user_id: str) -> List[str]:
    """Get list of product IDs in user's wishlist."""
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                "SELECT product_id FROM wishlists WHERE user_id = ?",
                (user_id,)
            )
            return [r["product_id"] for r in cursor.fetchall()]
    except Exception:
        return []


def init_database():
    """Initialize database with schema and sample data."""
    # Ensure database directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if database already has data
    if DB_PATH.exists():
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()["count"] > 0:
                # Database already initialized, skip seeding
                return
    
    # Create schema
    with get_connection() as conn:
        _create_schema(conn)
    
    # Initialize ID sequences
    with get_connection() as conn:
        # Set initial values matching dummy_db
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("ticket", 600)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("order", 500)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("product", 100)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("user", 200)
        )
    
    # Seed sample data
    with get_connection() as conn:
        # Sample users
        conn.execute(
            "INSERT INTO users (user_id, name, phone, email, created_at) VALUES (?, ?, ?, ?, ?)",
            ("u101", "Alex", "555-1234", "alex@example.com", "2025-11-01")
        )
        conn.execute(
            "INSERT INTO users (user_id, name, phone, email, created_at) VALUES (?, ?, ?, ?, ?)",
            ("u202", "Mehedi", "017xx-xxxxx", "mehedi@cartup.local", "2025-11-01")
        )
        conn.execute(
            "INSERT INTO users (user_id, name, phone, email, created_at) VALUES (?, ?, ?, ?, ?)",
            ("u303", "Sarah", "555-5678", "sarah@example.com", "2025-11-01")
        )
        
        # Sample products
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p001", "Smartphone", "Latest model smartphone with advanced features", 299.99, "Electronics", 1, 50)
        )
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p002", "Wireless Earbuds", "High-quality wireless earbuds with noise cancellation", 79.99, "Electronics", 1, 100)
        )
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p003", "Phone Case", "Protective case for smartphones", 19.99, "Accessories", 1, 200)
        )
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p004", "USB-C Charger", "Fast charging USB-C cable", 15.99, "Accessories", 1, 150)
        )
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p005", "Laptop", "High-performance laptop for work and gaming", 899.99, "Electronics", 1, 25)
        )
        
        # Sample orders
        conn.execute(
            "INSERT INTO orders (order_id, user_id, status, amount, delivery_date, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("o301", "u101", "Delivered", 320.00, "2025-11-06", "12 Baker Street, Dhaka", "2025-11-01")
        )
        conn.execute(
            "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
            ("o301", "Smartphone", 1)
        )
        conn.execute(
            "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
            ("o301", "Charger", 1)
        )
        
        conn.execute(
            "INSERT INTO orders (order_id, user_id, status, amount, delivery_date, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("o302", "u101", "In Transit", 79.99, "2025-11-10", "12 Baker Street, Dhaka", "2025-11-05")
        )
        conn.execute(
            "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
            ("o302", "Wireless Earbuds", 1)
        )
        
        conn.execute(
            "INSERT INTO orders (order_id, user_id, status, amount, delivery_date, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("o401", "u202", "Processing", 19.99, None, "SUST Hall, Sylhet", "2025-11-08")
        )
        conn.execute(
            "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
            ("o401", "Phone Case", 1)
        )
        
        conn.execute(
            "INSERT INTO orders (order_id, user_id, status, amount, delivery_date, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("o402", "u303", "Delivered", 899.99, "2025-11-07", "456 Main Street, New York", "2025-11-02")
        )
        conn.execute(
            "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
            ("o402", "Laptop", 1)
        )
        
        # Sample tickets
        conn.execute(
            "INSERT INTO tickets (ticket_id, order_id, issue, status, created_at) VALUES (?, ?, ?, ?, ?)",
            ("t501", "o301", "Damaged product", "Resolved", "2025-11-03")
        )
        
        # Sample recommendations
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u101", "Phone Case")
        )
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u101", "Wireless Earbuds")
        )
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u202", "USB-C Charger")
        )
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u202", "Phone Case")
        )
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u303", "Wireless Earbuds")
        )
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            ("u303", "USB-C Charger")
        )

