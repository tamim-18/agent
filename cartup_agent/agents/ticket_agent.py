"""
Support ticket agent - creates and tracks support tickets
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_current_order, to_greeter
from ..tools.ticket_tools import create_ticket, track_ticket, get_ticket_status


class TicketAgent(BaseAgent):
    """Agent that creates and tracks support tickets for orders."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You create and track support tickets for orders (missing, damaged, wrong item, etc.).\n"
                "Ask for order_id, issue description; create ticket; return ticket_id and status.\n"
                "If the user wants to check orders, process returns, or get recommendations, transfer to the appropriate agent.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_current_order, to_greeter, create_ticket, track_ticket, get_ticket_status],
            tts=google.TTS(voice_name="en-US-Chirp-HD-F", language="en-US"),  # Will be overridden by BaseAgent based on language
        )
    
    @function_tool()
    async def to_order(self, context: RunContext_T):
        """Transfer to OrderAgent for order-related queries."""
        return await self._transfer_to_agent("order", context)
    
    @function_tool()
    async def to_returns(self, context: RunContext_T):
        """Transfer to ReturnAgent for returns and refunds."""
        return await self._transfer_to_agent("returns", context)
    
    @function_tool()
    async def to_recommend(self, context: RunContext_T):
        """Transfer to RecommendAgent for product recommendations."""
        return await self._transfer_to_agent("recommend", context)
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when TicketAgent becomes active."""
        await self.session.generate_reply(
            instructions="Greet the user briefly and let them know you're here to help with their support issue. Mention you can create a ticket, track existing tickets, or check ticket status."
        )

