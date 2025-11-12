"""
Ticket-related tools for CartUp agent
"""

from typing import Annotated, Dict, Any
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T
from ..database.db import get_order, get_ticket, create_ticket_record
from ..utils.helpers import _next_id


@function_tool()
async def create_ticket(
    order_id: Annotated[str, Field(description="Related order ID. Must be lowercase format (e.g., o302).")],
    issue: Annotated[str, Field(description="Short issue description")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Create a ticket and return ticket data."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    order_id = order_id.lower().strip()
    order = get_order(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    
    ticket_id = _next_id("ticket")
    from datetime import datetime
    created_at = datetime.now().strftime("%Y-%m-%d")
    
    if create_ticket_record(ticket_id, order_id, issue, "Open", created_at):
        context.userdata.current_ticket_id = ticket_id
        context.userdata.current_order_id = order_id
        
        return {
            "ticket_id": ticket_id,
            "order_id": order_id,
            "issue": issue,
            "status": "Open",
        }
    else:
        return {"error": f"Failed to create ticket for order {order_id}"}


@function_tool()
async def track_ticket(
    ticket_id: Annotated[str, Field(description="Ticket ID to check (e.g., t602). Must be lowercase format.")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Fetch ticket status."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    ticket_id = ticket_id.lower().strip()
    ticket = get_ticket(ticket_id)
    if not ticket:
        return {"error": f"Ticket {ticket_id} not found"}
    
    context.userdata.current_ticket_id = ticket_id
    return {
        "ticket_id": ticket_id,
        **ticket,
    }


@function_tool()
async def get_ticket_status(
    ticket_id: Annotated[str, Field(description="Ticket ID to check. Must be lowercase format (e.g., t602).")],
    context: RunContext_T,
) -> Dict[str, Any]:
    """Get ticket status and details."""
    # Normalize to lowercase (handles cases where STT/LLM capitalizes IDs)
    ticket_id = ticket_id.lower().strip()
    return await track_ticket(ticket_id, context)

