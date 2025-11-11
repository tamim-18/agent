"""
Return and refund agent - handles returns and refunds
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_current_order, to_greeter
from ..tools.return_tools import initiate_return, get_return_status, update_refund_status


class ReturnAgent(BaseAgent):
    """Agent that manages returns and refunds."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You manage returns and refunds. Ask for order_id; mark a return as initiated; "
                "report return and refund status.\n"
                "If the user wants to check orders, create tickets, or get recommendations, transfer to the appropriate agent.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_current_order, to_greeter, initiate_return, get_return_status, update_refund_status],
            tts=google.TTS(voice_name="en-US-Chirp-HD-D", language="en-US"),  # Will be overridden by BaseAgent based on language
        )
    
    @function_tool()
    async def to_order(self, context: RunContext_T):
        """Transfer to OrderAgent for order-related queries."""
        return await self._transfer_to_agent("order", context)
    
    @function_tool()
    async def to_ticket(self, context: RunContext_T):
        """Transfer to TicketAgent for support ticket creation and tracking."""
        return await self._transfer_to_agent("ticket", context)
    
    @function_tool()
    async def to_recommend(self, context: RunContext_T):
        """Transfer to RecommendAgent for product recommendations."""
        return await self._transfer_to_agent("recommend", context)
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when ReturnAgent becomes active."""
        await self.session.generate_reply(
            instructions="Greet the user briefly and let them know you're here to help with returns and refunds. Mention you can initiate a return, check return status, or update refund information."
        )

