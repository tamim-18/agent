"""
Order-related tools for CartUp agent
"""

from typing import Annotated, Dict, Any, List
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T
from ..database.db import get_order, get_user, update_order_address


@function_tool()
async def get_order_details(
    order_id: Annotated[str, Field(description="Order ID to fetch (e.g., o302)")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Fetch order details from database."""
    order = get_order(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    context.userdata.current_order_id = order_id
    return {
        "order_id": order_id,
        "status": order["status"],
        "items": order["items"],
        "amount": order["amount"],
        "delivery_date": order.get("delivery_date"),
        "address": order.get("address", ""),
    }


@function_tool()
async def get_user_orders(
    user_id: Annotated[str, Field(description="User ID to fetch orders for (e.g., u101)")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Get all orders for a user."""
    user = get_user(user_id)
    if not user:
        return {"error": f"User {user_id} not found"}
    
    order_ids = user.get("orders", [])
    orders = []
    
    for order_id in order_ids:
        order = get_order(order_id)
        if order:
            orders.append({
                "order_id": order_id,
                "status": order["status"],
                "items": order["items"],
                "amount": order["amount"],
                "delivery_date": order.get("delivery_date"),
            })
    
    context.userdata.user_id = user_id
    return {
        "user_id": user_id,
        "orders": orders,
        "total_orders": len(orders),
    }


@function_tool()
async def update_delivery_address(
    order_id: Annotated[str, Field(description="Order ID to update")],
    new_address: Annotated[str, Field(description="New delivery address")],
    context: RunContext_T,
) -> str:
    """Update delivery address for an order (simulated)."""
    order = get_order(order_id)
    if not order:
        return f"Order {order_id} not found"
    
    if update_order_address(order_id, new_address):
        context.userdata.current_order_id = order_id
        return f"Address for order {order_id} updated to {new_address}"
    else:
        return f"Failed to update address for order {order_id}"

