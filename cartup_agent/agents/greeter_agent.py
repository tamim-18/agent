"""
Greeter agent - initial point of contact and routing agent
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

from .base_agent import BaseAgent
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_user, set_current_order


class GreeterAgent(BaseAgent):
    """Greeter agent that routes users to specialized agents."""
    
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant.\n"
                "IMPORTANT: Language is already selected (check userdata.language). Do NOT ask for language selection.\n"
                "GREETING RULES - Keep it concise and to the point:\n"
                "- ALWAYS start with the branding message: 'Welcome to Bangladesh number one e-commerce platform CartUp' (in the user's language)\n"
                "- Then immediately ask how you can help: 'How can I help you today?' or 'আমি আপনাকে কীভাবে সাহায্য করতে পারি?' (Bengali)\n"
                "- Keep the greeting short - no extra fluff or explanations\n"
                "BRANDING MESSAGES:\n"
                "- English: 'Welcome to Bangladesh number one e-commerce platform CartUp. How can I help you today?'\n"
                "- Bengali: 'স্বাগতম বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপে। আমি আপনাকে কীভাবে সাহায্য করতে পারি?'\n"
                "ROUTING:\n"
                "If they want: order tracking/modification ⇒ OrderAgent; issue/ticket ⇒ TicketAgent; "
                "returns/refunds ⇒ ReturnAgent; recommendations ⇒ RecommendAgent.\n"
                "Ask for user_id or order_id when needed and call the appropriate tools.\n"
                "Always respond in the user's selected language. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_user, set_current_order],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Despina", language="bn-IN", speaking_rate=1.1),
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
        """Generate a concise greeting when GreeterAgent becomes active after transfer."""
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say concisely: 'স্বাগতম বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপে। আমি আপনাকে কীভাবে সাহায্য করতে পারি?' Then wait for user response."
            )
        else:
            await self.session.generate_reply(
                instructions="Say concisely: 'Welcome to Bangladesh number one e-commerce platform CartUp. How can I help you today?' Then wait for user response."
            )

