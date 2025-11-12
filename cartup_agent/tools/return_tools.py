"""
Return and refund tools for CartUp agent
"""

from typing import Annotated, Dict, Any
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T
from ..database.db import get_order, get_return, create_return_record, update_refund_status as db_update_refund_status


@function_tool()
async def initiate_return(
    order_id: Annotated[str, Field(description="Order to return. Must be lowercase format (e.g., o302).")],
    reason: Annotated[str, Field(description="Why returning")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Create/overwrite a return record."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    order_id = order_id.lower().strip()
    order = get_order(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    from datetime import datetime
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    if create_return_record(order_id, reason, "Pending Courier Pickup", "Not Initiated", created_at):
        context.userdata.current_order_id = order_id
        return_record = get_return(order_id)
        return {
            "order_id": order_id,
            **return_record,
        }
    else:
        return {"error": f"Failed to create return for order {order_id}"}


@function_tool()
async def get_return_status(
    order_id: Annotated[str, Field(description="Order ID. Must be lowercase format (e.g., o302).")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Return current return status (if any)."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    order_id = order_id.lower().strip()
    return_record = get_return(order_id)
    if not return_record:
        return {"error": f"No return found for order {order_id}"}
    
    context.userdata.current_order_id = order_id
    return {
        "order_id": order_id,
        **return_record,
    }


@function_tool()
async def update_refund_status(
    order_id: Annotated[str, Field(description="Order ID. Must be lowercase format (e.g., o302).")],
    refund_status: Annotated[str, Field(description="New refund status")],
    context: RunContext_T,
) -> str:
    """Simulate refund progress update."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    order_id = order_id.lower().strip()
    return_record = get_return(order_id)
    if not return_record:
        return f"No return found for order {order_id}"
    
    if db_update_refund_status(order_id, refund_status):
        context.userdata.current_order_id = order_id
        return f"Refund status for order {order_id} set to {refund_status}"
    else:
        return f"Failed to update refund status for order {order_id}"

