"""
Return and refund agent - handles returns and refunds
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

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
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) and last tool results. "
                "If they are already present, do not re-ask and proceed.\n"
                "If the user wants to check orders, create tickets, or get recommendations, transfer to the appropriate agent.\n"
                "CONVERSATIONAL RESPONSES:\n"
                "- When explaining return status, use natural language. Say 'Your return is being processed' or 'We're arranging pickup for your return' "
                "rather than reading status codes like 'return_status: Pending Courier Pickup'.\n"
                "- When mentioning refund amounts, always use 'tk' (Taka). For example: 'Your refund of 5000 tk is being processed'.\n"
                "- When confirming return initiation, say something like 'I've initiated the return for your order o302' instead of "
                "reading out all return record fields verbatim.\n"
                "- Make it sound like you're personally helping them with their return, not just reading database information.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English.\n"
                "BENGALI EXAMPLES (when language is 'bn-BD'):\n"
                "- For return status: 'আপনার রিটার্ন প্রক্রিয়াধীন আছে' or 'আমরা আপনার রিটার্নের জন্য পিকআপের ব্যবস্থা করছি'.\n"
                "- For refund amounts: 'আপনার পাঁচ হাজার টাকার রিফান্ড প্রক্রিয়াধীন আছে'.\n"
                "- For return initiation: 'আমি আপনার o302 নম্বর অর্ডারের জন্য রিটার্ন শুরু করেছি'.\n"
                "- Use natural Bengali expressions: 'আমি আপনাকে সাহায্য করছি', 'চিন্তা করবেন না', 'আমি এখনই দেখছি'."
            ),
            tools=[
                set_current_order,
                to_greeter,
                initiate_return,
                get_return_status,
                update_refund_status,
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Despina", language="bn-IN"),  # Will be overridden by BaseAgent based on language
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
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say a very short intro in Bangladesh Bengali: 'হাই, আমি রিটার্ন এবং রিফান্ড এজেন্ট।' Then immediately proceed to help the user based on the context from the previous conversation in Bangladesh Bengali. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )
        else:
            await self.session.generate_reply(
                instructions="Say a very short intro: 'Hi, I'm the returns and refunds agent.' Then immediately proceed to help the user based on the context from the previous conversation. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )

