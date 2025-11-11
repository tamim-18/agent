"""
Greeter agent - initial point of contact and routing agent
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_user, set_current_order, set_language


class GreeterAgent(BaseAgent):
    """Greeter agent that routes users to specialized agents."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant.\n"
                "FIRST, check if the user has selected a language preference (check userdata.language). "
                "If no language is set, you MUST offer language selection: 'Would you like to continue in English or Bengali? Please say English or Bengali.' "
                "When the user responds with their choice, call the set_language tool with 'en-IN' for English or 'bn-BD' for Bangladesh Bengali.\n"
                "After language is selected, greet the caller warmly in the selected language and figure out what they need, then route them.\n"
                "If they want: order tracking/modification ⇒ OrderAgent; issue/ticket ⇒ TicketAgent; "
                "returns/refunds ⇒ ReturnAgent; recommendations ⇒ RecommendAgent.\n"
                "Ask for user_id or order_id when needed and call the appropriate tools.\n"
                "Always respond in the user's selected language. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_user, set_current_order, set_language],
            llm=openai.LLM(model="gpt-4o-mini"),
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
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when GreeterAgent becomes active after transfer."""
        userdata = self.session.userdata
        if not userdata.language:
            # If language not set, prompt for selection
            await self.session.generate_reply(
                instructions="Welcome back! Would you like to continue in English or Bengali? Please say 'English' or 'Bengali'."
            )
        else:
            # Language is set, greet normally
            lang_name = "English" if userdata.language == "en-IN" else "Bengali (Bangladesh)"
            await self.session.generate_reply(
                instructions=f"Welcome back! How can I help you today? (Responding in {lang_name})"
            )

