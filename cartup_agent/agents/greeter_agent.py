"""
Greeter agent - initial point of contact and routing agent
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_user, set_current_order


class GreeterAgent(BaseAgent):
    """Greeter agent that routes users to specialized agents."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant.\n"
                "Your job is to greet the caller, figure out what they need, and route them.\n"
                "If they want: order tracking/modification ⇒ OrderAgent; issue/ticket ⇒ TicketAgent; "
                "returns/refunds ⇒ ReturnAgent; recommendations ⇒ RecommendAgent.\n"
                "Ask for user_id or order_id when needed and call the appropriate tools."
            ),
            tools=[set_user, set_current_order],
            llm=google.LLM(model="gemini-2.0-flash"),
            tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
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
    
    @function_tool()
    async def to_recommend(self, context: RunContext_T):
        """Transfer to RecommendAgent for product recommendations."""
        return await self._transfer_to_agent("recommend", context)

