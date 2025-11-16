"""
Order management agent - handles order queries and updates
"""

import logging
from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

from .base_agent import BaseAgent    
from ..session.user_data import RunContext_T
from ..tools.common_tools import set_current_order, to_greeter  
from ..tools.order_tools import get_order_details, get_user_orders, update_delivery_address

logger = logging.getLogger("cartup-agent")  


class OrderAgent(BaseAgent):
    """Agent that handles order queries: status, items, amount, ETA, address updates."""
    
    def __init__(self, language: str = "en-IN") -> None:
        # Dynamic TTS based on language
        if language == "bn-BD":
            tts_config = google.TTS(voice_name="bn-IN-Chirp3-HD-Aoede", language="bn-IN", speaking_rate=1.1)
            #logger.info(f"[OrderAgent] TTS configured: Bengali voice 'bn-IN-Chirp3-HD-Despina' (language: bn-IN)")
        else:
            tts_config = google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN", speaking_rate=1)
            #logger.info(f"[OrderAgent] TTS configured: English voice 'en-IN-Chirp3-HD-Algenib' (language: en-IN)")
        
        super().__init__(
            instructions=(
                "Start by introducing yourself: 'Hi, I’m Tanisha (তানিশা), CartUp's order support assistant.'\n"
                "You handle order queries: status, items, amount, ETA, address updates.\n"
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) and last tool results. "
                "If they are already present, do not re-ask and proceed.\n"
                "If user_id or order_id is missing, politely ask and then call tools.\n"
                "If the user wants to create tickets, process returns, or get recommendations, transfer to the appropriate agent.\n"
                "CONVERSATIONAL RESPONSES:\n"
                "- When sharing order details, speak naturally like a customer service agent. "
                "Instead of listing raw data like 'order_id: o302, status: Pending', say 'Your order o302 is currently pending' or 'I can see your order is being prepared'.\n"
                "- When mentioning amounts, always use 'tk' (Taka) as the currency. For example: 'The total is 5000 tk' or 'Your order amount is 2500 tk'.\n"
                "- When listing items, describe them naturally. Instead of reading item dictionaries verbatim, say 'You've ordered a Laptop and 2 Mice' or 'Your order includes 3 items'.\n"
                "- Make it sound like you're personally helping the customer, not reading from a database.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English.\n"
                "BENGALI EXAMPLES (when language is 'bn-BD'):\n"
                "- Instead of 'order_id: o302, status: Pending', say 'আপনার o302 নম্বর অর্ডারটি এখনো প্রক্রিয়াধীন আছে' or 'আপনার অর্ডার প্রস্তুত হচ্ছে'.\n"
                "- For amounts: 'মোট পাঁচ হাজার টাকা' or 'আপনার অর্ডারের পরিমাণ আড়াই হাজার টাকা'.\n"
                "- For items: 'আপনি একটি ল্যাপটপ এবং দুটি মাউস অর্ডার করেছেন' or 'আপনার অর্ডারে তিনটি আইটেম আছে'.\n"
                "- Use natural Bengali expressions: 'জি, আমি দেখছি', 'আপনার অর্ডার এখনো প্রক্রিয়াধীন', 'আমি আপনাকে সাহায্য করতে পারি'."
            ),
            tools=[
                set_current_order,
                to_greeter,
                get_order_details,
                get_user_orders,
                update_delivery_address,
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=tts_config,
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
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        logger.info(f"[OrderAgent] Generating transfer greeting with language: {language} (from userdata.language: {userdata.language})")
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say a very short intro in Bangladesh Bengali: 'হাই, আমি তানিশা, কার্টআপের অর্ডার সাপোর্ট অ্যাসিস্ট্যান্ট।।' Then immediately proceed to help the user based on the context from the previous conversation in Bangladesh Bengali. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )
        else:
            await self.session.generate_reply(
                instructions="Say a very short intro: 'Hi, I'm Tanisha, CartUp's order support assistant.' Then immediately proceed to help the user based on the context from the previous conversation. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )
