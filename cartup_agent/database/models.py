"""
Data models for CartUp database
Type definitions and schemas for all entities
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class User:
    """User model"""
    user_id: str
    name: str
    phone: str
    email: str
    orders: List[str] = None  # List of order IDs
    
    def __post_init__(self):
        if self.orders is None:
            self.orders = []


@dataclass
class Product:
    """Product model"""
    product_id: str
    name: str
    description: str
    price: float
    category: str
    in_stock: bool = True
    stock_quantity: int = 0


@dataclass
class Order:
    """Order model"""
    order_id: str
    user_id: str
    status: str  # Processing, In Transit, Delivered, Cancelled
    items: List[str]  # List of product names or IDs
    amount: float
    delivery_date: Optional[str] = None
    address: str = ""
    created_at: Optional[str] = None


@dataclass
class Ticket:
    """Support ticket model"""
    ticket_id: str
    order_id: str
    issue: str
    status: str  # Open, In Progress, Resolved, Closed
    created_at: Optional[str] = None


@dataclass
class Return:
    """Return/refund model"""
    order_id: str
    status: str  # Pending Courier Pickup, In Transit, Received, Processed
    refund_status: str  # Not Initiated, Processing, Completed, Refunded
    reason: str = ""
    created_at: Optional[str] = None


@dataclass
class Cart:
    """Shopping cart model"""
    user_id: str
    items: List[dict] = None  # List of {product_id, quantity, price}
    total: float = 0.0
    
    def __post_init__(self):
        if self.items is None:
            self.items = []


@dataclass
class Wishlist:
    """Wishlist model"""
    user_id: str
    product_ids: List[str] = None
    
    def __post_init__(self):
        if self.product_ids is None:
            self.product_ids = []

