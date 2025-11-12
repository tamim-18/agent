"""
Support ticket agent - creates and tracks support tickets
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

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
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) and last tool results. "
                "If they are already present, do not re-ask and proceed.\n"
                "Ask for order_id, issue description; create ticket; return ticket_id and status.\n"
                "If the user wants to check orders, process returns, or get recommendations, transfer to the appropriate agent.\n"
                "CONVERSATIONAL RESPONSES:\n"
                "- When sharing ticket status, speak conversationally. Say 'I've created a ticket for you' or 'Your ticket is currently being reviewed' "
                "rather than reading out ticket IDs and status codes verbatim.\n"
                "- When confirming ticket creation, say something like 'I've created ticket t602 for your order o302' instead of "
                "'ticket_id: t602, order_id: o302, status: Open'.\n"
                "- Make it sound like you're personally handling their issue, not just reading database records.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English.\n"
                "BENGALI EXAMPLES (when language is 'bn-BD'):\n"
                "- For ticket status: 'আমি আপনার জন্য একটি টিকেট তৈরি করেছি' or 'আপনার টিকেটটি এখন পর্যালোচনা করা হচ্ছে'.\n"
                "- For ticket creation: 'আমি আপনার o302 নম্বর অর্ডারের জন্য t602 নম্বর টিকেট তৈরি করেছি' instead of "
                "'ticket_id: t602, order_id: o302, status: Open'.\n"
                "- Use natural Bengali expressions: 'আমি আপনার সমস্যা সমাধান করছি', 'চিন্তা করবেন না', 'আমি এখনই দেখছি'."
            ),
            tools=[
                set_current_order,
                to_greeter,
                create_ticket,
                track_ticket,
                get_ticket_status,
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Despina", language="bn-IN"),  # Align with other agents' English TTS
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
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say a very short intro in Bangladesh Bengali: 'হাই, আমি সাপোর্ট টিকেট এজেন্ট।' Then immediately proceed to help the user based on the context from the previous conversation in Bangladesh Bengali. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )
        else:
            await self.session.generate_reply(
                instructions="Say a very short intro: 'Hi, I'm the support ticket agent.' Then immediately proceed to help the user based on the context from the previous conversation. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )

