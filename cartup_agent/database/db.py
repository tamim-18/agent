"""
SQLite database implementation for CartUp agent
Replaces the in-memory DUMMY_DB with persistent storage
"""

import sqlite3
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from pathlib import Path

from .seed_data import (
    get_seed_users,
    get_seed_products,
    get_seed_orders,
    get_seed_tickets,
    get_seed_returns,
    get_seed_recommendations,
    get_seed_wishlists,
)

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


def _seed_database(conn: sqlite3.Connection):
    """Seed database with sample data from seed_data module."""
    # Seed users
    users = get_seed_users()
    for user_data in users:
        conn.execute(
            "INSERT INTO users (user_id, name, phone, email, created_at) VALUES (?, ?, ?, ?, ?)",
            user_data
        )
    
    # Seed products
    products = get_seed_products()
    for product_data in products:
        conn.execute(
            "INSERT INTO products (product_id, name, description, price, category, in_stock, stock_quantity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            product_data
        )
    
    # Seed orders and order items
    orders = get_seed_orders()
    for order_data in orders:
        conn.execute(
            "INSERT INTO orders (order_id, user_id, status, amount, delivery_date, address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                order_data["order_id"],
                order_data["user_id"],
                order_data["status"],
                order_data["amount"],
                order_data["delivery_date"],
                order_data["address"],
                order_data["created_at"],
            )
        )
        # Insert order items
        for item_name, quantity in order_data["items"]:
            conn.execute(
                "INSERT INTO order_items (order_id, product_name, quantity) VALUES (?, ?, ?)",
                (order_data["order_id"], item_name, quantity)
            )
    
    # Seed tickets
    tickets = get_seed_tickets()
    for ticket_data in tickets:
        conn.execute(
            "INSERT INTO tickets (ticket_id, order_id, issue, status, created_at) VALUES (?, ?, ?, ?, ?)",
            ticket_data
        )
    
    # Seed returns
    returns = get_seed_returns()
    for return_data in returns:
        conn.execute(
            "INSERT INTO returns (order_id, status, refund_status, reason, created_at) VALUES (?, ?, ?, ?, ?)",
            return_data
        )
    
    # Seed recommendations
    recommendations = get_seed_recommendations()
    for rec_data in recommendations:
        conn.execute(
            "INSERT INTO recommendations (user_id, product_name) VALUES (?, ?)",
            rec_data
        )
    
    # Seed wishlists
    wishlists = get_seed_wishlists()
    for wishlist_data in wishlists:
        conn.execute(
            "INSERT INTO wishlists (user_id, product_id) VALUES (?, ?)",
            wishlist_data
        )


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
        # Set initial values to accommodate seed data
        # Users: up to u125, Orders: up to o325, Products: up to p025, Tickets: up to t525
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("ticket", 600)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("order", 400)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("product", 30)
        )
        conn.execute(
            "INSERT OR IGNORE INTO id_sequences (entity_type, next_value) VALUES (?, ?)",
            ("user", 130)
        )
    
    # Seed sample data using modular seed_data module
    with get_connection() as conn:
        _seed_database(conn)

