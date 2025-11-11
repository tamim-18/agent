"""
Order management agent - handles order queries and updates
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_current_order, to_greeter
from ..tools.order_tools import get_order_details, get_user_orders, update_delivery_address


class OrderAgent(BaseAgent):
    """Agent that handles order queries: status, items, amount, ETA, address updates."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You handle order queries: status, items, amount, ETA, address updates.\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) and last tool results. "
                "If they are already present, do not re-ask and proceed.\n"
                "If user_id or order_id is missing, politely ask and then call tools.\n"
                "If the user wants to create tickets, process returns, or get recommendations, transfer to the appropriate agent.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[
                set_current_order,
                to_greeter,
                get_order_details,
                get_user_orders,
                update_delivery_address,
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-D", language="en-IN"),  # Will be overridden by BaseAgent based on language
        )
    
    @function_tool()
    async def to_ticket(self, context: RunContext_T):
        """Transfer to TicketAgent for support ticket creation and tracking."""
        return await self._transfer_to_agent("ticket", context)
    
    @function_tool()
    async def to_returns(self, context: RunContext_T):
        """Transfer to ReturnAgent for returns and refunds."""
        return await self._transfer_to_agent("returns", context)
    
    @function_tool()
    async def to_recommend(self, context: RunContext_T):
        """Transfer to RecommendAgent for product recommendations."""
        return await self._transfer_to_agent("recommend", context)
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when OrderAgent becomes active."""
        await self.session.generate_reply(
            instructions="Greet the user briefly and let them know you're here to help with their order. Mention you can check order status, details, delivery addresses, or order history."
        )

