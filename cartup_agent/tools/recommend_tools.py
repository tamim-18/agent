"""
Product recommendation tools for CartUp agent
"""

from typing import Annotated, Dict, Any, List
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T
from ..database.db import get_user, get_product, get_recommendations_for_user, get_wishlist_for_user, add_to_wishlist as db_add_to_wishlist


@function_tool()
async def get_recommendations(
    user_id: Annotated[str, Field(description="User ID to recommend for. Must be lowercase format (e.g., u101).")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Fetch recommended items for a user."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    user_id = user_id.lower().strip()
    recommendations = get_recommendations_for_user(user_id)
    context.userdata.user_id = user_id
    return {
        "user_id": user_id,
        "recommendations": recommendations,
    }


@function_tool()
async def get_product_details(
    product_id: Annotated[str, Field(description="Product ID to fetch (e.g., p001). Must be lowercase format.")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Get product information."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    product_id = product_id.lower().strip()
    product = get_product(product_id)
    if not product:
        return {"error": f"Product {product_id} not found"}
    
    context.userdata.current_product_id = product_id
    return {
        "product_id": product_id,
        "name": product["name"],
        "description": product["description"],
        "price": product["price"],
        "category": product["category"],
        "in_stock": product["in_stock"],
    }


@function_tool()
async def add_to_wishlist(
    user_id: Annotated[str, Field(description="User ID. Must be lowercase format (e.g., u101).")],
    product_id: Annotated[str, Field(description="Product ID to add. Must be lowercase format (e.g., p001).")],
    context: RunContext_T,
) -> str:
    """Add a product to user's wishlist."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    user_id = user_id.lower().strip()
    product_id = product_id.lower().strip()
    product = get_product(product_id)
    if not product:
        return f"Product {product_id} not found"
    
    if db_add_to_wishlist(user_id, product_id):
        context.userdata.user_id = user_id
        context.userdata.current_product_id = product_id
        return f"Product {product_id} ({product['name']}) added to wishlist for user {user_id}"
    else:
        return f"Failed to add product {product_id} to wishlist for user {user_id}"

