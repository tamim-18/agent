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
    
    def __init__(self, language: str = "en-IN") -> None:
        import logging
        logger = logging.getLogger("cartup-agent")
        
        # Dynamic TTS based on language
        if language == "bn-BD":
            tts_config = google.TTS(voice_name="bn-IN-Chirp3-HD-Despina", language="bn-IN", speaking_rate=1.1)
            #logger.info(f"[GreeterAgent] TTS configured: Bengali voice 'bn-IN-Chirp3-HD-Despina' (language: bn-IN)")
        else:
            tts_config = google.TTS(voice_name="en-IN-Chirp3-HD-Despina", language="en-IN", speaking_rate=1.1)
            #logger.info(f"[GreeterAgent] TTS configured: English voice 'en-IN-Chirp3-HD-Algenib' (language: en-IN)")
        
        super().__init__(
            instructions=(
                "You are CartUp's friendly voice assistant. Your name is Nawme (নাওমে).\n"
                "IMPORTANT: Language is already selected (check userdata.language). Do NOT ask for language selection.\n"
                "GREETING RULES - Keep it concise and to the point:\n"
                "- ALWAYS start with the branding message: 'Welcome to Bangladesh number one e-commerce platform CartUp' (in the user's language)\n"
                "- Then immediately ask how you can help: 'How can I help you today?' or 'আমি আপনাকে কীভাবে সাহায্য করতে পারি?' (Bengali)\n"
                "- Keep the greeting short - no extra fluff or explanations\n"
                "BRANDING MESSAGES:\n"
                "- English: 'Welcome to Bangladesh number one e-commerce platform CartUp. How can I help you today?'\n"
                "- Bengali: 'স্বাগতম বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপে। আমি আপনাকে কীভাবে সাহায্য করতে পারি?'\n"
                "ROUTING - CRITICAL: DO NOT handle queries yourself. ALWAYS transfer to specialized agents immediately.\n"
                "ROUTING PRIORITY RULES:\n"
                "- If user mentions 'order', 'track order', 'order status', 'order ID', 'order details', 'order history', 'order modification' → IMMEDIATELY CALL to_order() tool\n"
                "- If user explicitly says 'transfer to order agent' or 'order agent' → IMMEDIATELY CALL to_order() tool\n"
                "- Order tracking queries ALWAYS go to OrderAgent, NOT TicketAgent\n"
                "- Only use to_ticket() if user explicitly wants to CREATE a NEW support ticket for a problem (damaged item, wrong item, missing item)\n"
                "ENGLISH ROUTING EXAMPLES:\n"
                "- 'I want to track my order' → CALL to_order()\n"
                "- 'Check my order status' → CALL to_order()\n"
                "- 'What's my order ID 0301?' → CALL to_order()\n"
                "- 'Transfer me to order agent' → CALL to_order()\n"
                "- 'I want to modify my order' → CALL to_order()\n"
                "- 'Create a ticket for damaged product' → CALL to_ticket()\n"
                "- 'I want to return my order' → CALL to_returns()\n"
                "- 'Recommend me products' → CALL to_recommend()\n"
                "BENGALI ROUTING EXAMPLES (when language is 'bn-BD'):\n"
                "- 'আমার অর্ডার ট্র্যাক করতে চাই' → CALL to_order()\n"
                "- 'অর্ডার দেখতে চাই' → CALL to_order()\n"
                "- 'অর্ডারের অবস্থা জানতে চান' → CALL to_order()\n"
                "- 'অর্ডার আইডি 0301' → CALL to_order()\n"
                "- 'অর্ডার এজেন্টে যেতে চাই' → CALL to_order()\n"
                "- 'অর্ডার পরিবর্তন করতে চাই' → CALL to_order()\n"
                "- 'নষ্ট পণ্যের জন্য টিকেট তৈরি করতে চাই' → CALL to_ticket()\n"
                "- 'অর্ডার রিটার্ন করতে চাই' → CALL to_returns()\n"
                "- 'পণ্যের সুপারিশ চাই' → CALL to_recommend()\n"
                "TOOL USAGE:\n"
                "- Use set_user() if user_id is needed\n"
                "- Use set_current_order() if order_id is needed\n"
                "- DO NOT ask for user_id or order_id yourself - let the specialized agents handle that\n"
                "- Your ONLY job is to identify intent and transfer immediately\n"
                "Always respond in the user's selected language. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English."
            ),
            tools=[set_user, set_current_order],
            llm=openai.LLM(model="gpt-4o-mini"),
            tts=tts_config,
        )
    
    @function_tool()
    async def to_order(self, context: RunContext_T):
        """Transfer to OrderAgent for order-related queries.
        
        Use this tool IMMEDIATELY when user mentions:
        - Order tracking, order status, order details, order history
        - Order ID lookup, order modification
        - English: 'track order', 'order status', 'check order', 'order details'
        - Bengali: 'অর্ডার ট্র্যাক', 'অর্ডার দেখতে', 'অর্ডারের অবস্থা', 'অর্ডার আইডি'
        - User explicitly says 'transfer to order agent' or 'order agent'
        
        DO NOT use this for creating support tickets - use to_ticket() instead."""
        return await self._transfer_to_agent("order", context)
    
    @function_tool()
    async def to_ticket(self, context: RunContext_T):
        """Transfer to TicketAgent for creating NEW support tickets for problems.
        
        Use this tool ONLY when user explicitly wants to CREATE a support ticket for:
        - Damaged product, wrong item received, missing item
        - English: 'create ticket', 'file complaint', 'report problem'
        - Bengali: 'টিকেট তৈরি', 'সমস্যা রিপোর্ট', 'অভিযোগ'
        
        DO NOT use this for order tracking - use to_order() instead."""
        return await self._transfer_to_agent("ticket", context)
    
    @function_tool()
    async def to_returns(self, context: RunContext_T):
        """Transfer to ReturnAgent for returns and refunds.
        
        Use this tool when user wants to:
        - Return an order, request refund, cancel order
        - English: 'return order', 'refund', 'cancel order'
        - Bengali: 'অর্ডার রিটার্ন', 'রিফান্ড', 'অর্ডার বাতিল'"""
        return await self._transfer_to_agent("returns", context)
    
    @function_tool()
    async def to_recommend(self, context: RunContext_T):
        """Transfer to RecommendAgent for product recommendations.
        
        Use this tool when user wants:
        - Product suggestions, recommendations, what to buy
        - English: 'recommend products', 'suggest items', 'what should I buy'
        - Bengali: 'পণ্যের সুপারিশ', 'কী কিনব', 'সাজেশন'"""
        return await self._transfer_to_agent("recommend", context)
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a concise greeting when GreeterAgent becomes active after transfer."""
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say concisely: 'স্বাগতম বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপে। আমি নাওমে, কার্টআপের গ্রীটার এজেন্ট। আমি আপনাকে কীভাবে সাহায্য করতে পারি?' Then wait for user response."
            )
        else:
            await self.session.generate_reply(
                instructions="Say concisely: 'Welcome to Bangladesh number one e-commerce platform CartUp. I'm Nawme, CartUp's greeter agent. How can I help you today?' Then wait for user response."
            )

