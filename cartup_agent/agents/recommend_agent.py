"""
Product recommendation agent - provides personalized recommendations
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_user, to_greeter
from ..tools.recommend_tools import get_recommendations, get_product_details, add_to_wishlist


class RecommendAgent(BaseAgent):
    """Agent that provides personalized product recommendations."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You provide simple personalized recommendations using a dummy profile list. "
                "Ask for user_id if missing. Offer to add to wishlist (simulated). "
                "If the user wants to check orders, create tickets, or process returns, transfer to the appropriate agent."
            ),
            tools=[set_user, to_greeter, get_recommendations, get_product_details, add_to_wishlist],
            tts=google.TTS(voice_name="en-AU-Chirp-HD-F", language="en-AU"),
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
    async def to_returns(self, context: RunContext_T):
        """Transfer to ReturnAgent for returns and refunds."""
        return await self._transfer_to_agent("returns", context)
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when RecommendAgent becomes active."""
        await self.session.generate_reply(
            instructions="Greet the user briefly and let them know you're here to help with product recommendations. Mention you can provide personalized recommendations, show product details, or help add items to their wishlist."
        )

