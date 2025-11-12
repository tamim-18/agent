"""
Product recommendation agent - provides personalized recommendations
"""

from livekit.agents.llm import function_tool
from livekit.plugins import google, openai

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
                "Before asking for user_id or order_id, FIRST check the session summary (userdata) and last tool results. "
                "If they are already present, do not re-ask and proceed.\n"
                "If the user wants to check orders, create tickets, or process returns, transfer to the appropriate agent.\n"
                "CONVERSATIONAL RESPONSES:\n"
                "- When recommending products, describe them naturally. Instead of reading product IDs and technical specs verbatim, "
                "speak about benefits and features in a friendly way. Say 'I think you'd love this Laptop - it's perfect for your needs' "
                "instead of 'product_id: p001, name: Laptop, description: ...'.\n"
                "- When mentioning prices, always use 'tk' (Taka). For example: 'This product is available for 25000 tk' or 'The price is 5000 tk'.\n"
                "- When listing recommendations, present them conversationally. Say 'Based on your preferences, I'd recommend these 3 products' "
                "instead of reading out a list of product dictionaries.\n"
                "- Make recommendations sound personal and helpful, like a friendly sales associate, not a database query result.\n"
                "IMPORTANT: Always respond in the user's selected language. Check userdata.language for the current language preference. "
                "If language is 'bn-BD', respond in Bangladesh Bengali with authentic Bangladesh accent, pronunciation, and cultural context. "
                "If 'en-IN', respond in English.\n"
                "BENGALI EXAMPLES (when language is 'bn-BD'):\n"
                "- For product recommendations: 'আমার মনে হচ্ছে আপনি এই ল্যাপটপটি পছন্দ করবেন - এটি আপনার প্রয়োজনের জন্য পারফেক্ট' "
                "instead of 'product_id: p001, name: Laptop, description: ...'.\n"
                "- For prices: 'এই পণ্যটি পঁচিশ হাজার টাকায় পাওয়া যাচ্ছে' or 'দাম পাঁচ হাজার টাকা'.\n"
                "- For recommendations list: 'আপনার পছন্দ অনুযায়ী, আমি এই তিনটি পণ্য সুপারিশ করব'.\n"
                "- Use natural Bengali expressions: 'আমি মনে করি', 'আপনার জন্য ভাল হবে', 'এটি দেখে নিন'."
            ),
            tools=[
                set_user,
                to_greeter,
                get_recommendations,
                get_product_details,
                add_to_wishlist,
            ],
            llm=openai.LLM(model="gpt-4o-mini"),
            # Use a different Bengali voice optimized for recommendations (warmer, friendlier tone)
            # Trying "Aoede" voice which may sound better for product recommendations
            tts=google.TTS(voice_name="bn-IN-Chirp3-HD-Pulcherrima", language="bn-IN"),
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
        userdata = self.session.userdata
        language = userdata.language or "en-IN"
        
        if language == "bn-BD":
            await self.session.generate_reply(
                instructions="Say a very short intro in Bangladesh Bengali: 'হাই, আমি রিকমেন্ডেশন এজেন্ট।' Then immediately proceed to help the user based on the context from the previous conversation in Bangladesh Bengali. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )
        else:
            await self.session.generate_reply(
                instructions="Say a very short intro: 'Hi, I'm the recommendation agent.' Then immediately proceed to help the user based on the context from the previous conversation. Don't list capabilities, just identify yourself briefly and continue with what they need."
            )

