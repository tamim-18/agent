"""
Common tools shared across all CartUp agents
"""

from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T


@function_tool()
async def set_user(
    user_id: Annotated[str, Field(description="The authenticated/assumed user id (e.g., u101)")],
    context: RunContext_T,
) -> str:
    """Attach a known user_id to the session (simulates auth / caller lookup)."""
    context.userdata.user_id = user_id
    return f"User set to {user_id}"


@function_tool()
async def set_current_order(
    order_id: Annotated[str, Field(description="Order id to focus on (e.g., o302)")],
    context: RunContext_T,
) -> str:
    """Set the focal order id for follow-up queries (track/modify)."""
    context.userdata.current_order_id = order_id
    return f"Current order set to {order_id}"


@function_tool()
async def to_greeter(context: RunContext_T) -> tuple:
    """Route caller back to the GreeterAgent."""
    curr_agent = context.session.current_agent
    if hasattr(curr_agent, "_transfer_to_agent"):
        return await curr_agent._transfer_to_agent("greeter", context)
    return curr_agent, "Returning to greeter."

