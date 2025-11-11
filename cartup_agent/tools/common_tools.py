"""
Common tools shared across all CartUp agents
"""

from typing import Annotated
from pydantic import Field
from livekit.agents.llm import function_tool

from ..session.user_data import RunContext_T
from ..config import get_tts_for_language


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
async def set_language(
    language: Annotated[str, Field(description="Language code: 'en-IN' for English or 'bn-BD' for Bangladesh Bengali")],
    context: RunContext_T,
) -> str:
    """Set the preferred language for the conversation session."""
    if language not in ["en-IN", "bn-BD"]:
        return f"Invalid language code. Please use 'en-IN' for English or 'bn-BD' for Bangladesh Bengali."
    context.userdata.language = language
    
    # Try to update session TTS if possible (may not be supported)
    try:
        tts_instance = get_tts_for_language(language)
        # Attempt to update session TTS (this may not work if TTS is read-only)
        if hasattr(context.session, 'tts') and hasattr(context.session.tts, '__setattr__'):
            try:
                context.session.tts = tts_instance
            except (AttributeError, TypeError):
                # TTS is read-only, which is expected
                pass
    except Exception:
        # If TTS update fails, continue anyway - language preference is set
        pass
    
    lang_name = "English" if language == "en-IN" else "Bengali (Bangladesh)"
    return f"Language set to {lang_name} ({language}). All responses will now be in {lang_name} with authentic Bangladesh accent and cultural context."


@function_tool()
async def to_greeter(context: RunContext_T) -> tuple:
    """Route caller back to the GreeterAgent."""
    curr_agent = context.session.current_agent
    if hasattr(curr_agent, "_transfer_to_agent"):
        return await curr_agent._transfer_to_agent("greeter", context)
    return curr_agent, "Returning to greeter."

