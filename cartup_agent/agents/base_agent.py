"""
Base agent class with shared functionality for all CartUp agents
Handles context handoff and agent transfers
"""

import logging
from typing import Tuple
from livekit.agents.voice import Agent

from ..session.user_data import UserData, RunContext_T
from ..config import get_tts_for_language

logger = logging.getLogger("cartup-agent")


class BaseAgent(Agent):
    """Base class for all CartUp agents with shared functionality."""
    
    async def on_enter(self) -> None:
        """Called when agent becomes active. Handles context handoff."""
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")
        
        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        
        # Get language preference (default to English if not set)
        language = userdata.language or "en-IN"
        
        # Note: Agent's TTS is read-only and set during initialization.
        # The session-level TTS will be used, and we configure language-aware TTS
        # by ensuring the agent's instructions include language context.
        # For future enhancement, we could update session.tts if supported.
        
        # Copy truncated chat history from previous agent
        if isinstance(userdata.prev_agent, Agent):
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True,
                exclude_function_call=False
            ).truncate(max_items=10)
            
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [
                item for item in truncated_chat_ctx.items
                if item.id not in existing_ids
            ]
            chat_ctx.items.extend(items_copy)
        
        # Inject live summary for fast grounding with language context
        if language == "bn-BD":
            lang_name = "Bengali (Bangladesh)"
            lang_instructions = (
                f"IMPORTANT: Respond in Bengali with Bangladesh accent and cultural context ({language}). "
                f"The user has selected Bangladesh Bengali as their preferred language. "
                f"Use Bangladesh Bengali pronunciation, vocabulary, and cultural references. "
                f"All your responses must be in Bangladesh Bengali with authentic Bangladesh accent. "
                f"When greeting users, use appropriate Bangladesh Bengali greetings like 'আসসালামু আলাইকুম' (Assalamu Alaikum) or 'নমস্কার' (Namaskar). "
                f"Use Bangladesh-specific cultural references, vocabulary, and expressions throughout your responses.\n\n"
                f"বাংলায় কথা বলার নির্দেশনা (Instructions for Speaking in Bengali):\n"
                f"- প্রাকৃতিকভাবে কথা বলুন, যেন আপনি একজন বন্ধুত্বপূর্ণ বাংলাদেশি গ্রাহক সেবা প্রতিনিধি। "
                f"কথা বলার সময় স্বাভাবিক, সহজ এবং বন্ধুত্বপূর্ণ ভাষা ব্যবহার করুন।\n"
                f"- উচ্চারণ: বাংলাদেশি বাংলা উচ্চারণ ব্যবহার করুন। 'তুমি' বলুন 'তুমি' হিসেবে, 'আপনি' বলুন 'আপনি' হিসেবে। "
                f"শব্দগুলো স্পষ্ট এবং প্রাকৃতিকভাবে উচ্চারণ করুন।\n"
                f"- বাক্য গঠন: ছোট এবং সহজ বাক্য ব্যবহার করুন। দীর্ঘ এবং জটিল বাক্য এড়িয়ে চলুন। "
                f"উদাহরণ: 'আপনার অর্ডার o302 বর্তমানে প্রক্রিয়াধীন আছে' - এটি ভাল। "
                f"'আপনার অর্ডার যার আইডি হলো o302 এবং যেটি বর্তমানে আমাদের সিস্টেমে প্রক্রিয়াধীন অবস্থায় রয়েছে' - এটি খুব দীর্ঘ, এড়িয়ে চলুন।\n"
                f"- সাধারণ অভিব্যক্তি ব্যবহার করুন: 'জি, অবশ্যই', 'আচ্ছা', 'ঠিক আছে', 'ধন্যবাদ', 'আপনাকে সাহায্য করতে পেরে খুশি হলাম' ইত্যাদি।\n"
                f"- সংখ্যা এবং পরিমাণ: সংখ্যাগুলো বাংলায় বলুন। উদাহরণ: 'পাঁচ হাজার টাকা', 'তিনটি আইটেম', 'দুই দিন'।\n"
                f"- প্রশ্ন করার সময়: 'আপনার অর্ডার আইডি কী?' এর পরিবর্তে 'অর্ডার আইডি জানাবেন?' বা 'কোন অর্ডার নিয়ে জানতে চান?' "
                f"এমন প্রাকৃতিক প্রশ্ন ব্যবহার করুন।\n"
                f"- তথ্য দেওয়ার সময়: 'আপনার অর্ডার o302 বর্তমানে পেন্ডিং আছে' এর পরিবর্তে 'আপনার o302 নম্বর অর্ডারটি এখনো প্রক্রিয়াধীন আছে' "
                f"এমন প্রাকৃতিকভাবে বলুন।\n"
                f"- টাকা (Currency): সবসময় 'টাকা' বা 'tk' ব্যবহার করুন, 'রুপি' নয়। উদাহরণ: 'মোট পাঁচ হাজার টাকা' বা '৫০০০ tk'।\n"
                f"- বন্ধুত্বপূর্ণ এবং সহায়ক হন: গ্রাহককে সাহায্য করতে ইচ্ছুক এবং বন্ধুত্বপূর্ণ ভাব প্রকাশ করুন। "
                f"'আমি আপনাকে সাহায্য করতে পারি', 'চিন্তা করবেন না', 'আমি এখনই দেখে নিচ্ছি' ইত্যাদি ব্যবহার করুন।\n"
                f"- প্রাকৃতিক কথোপকথন: যেন আপনি একজন বন্ধুর সাথে কথা বলছেন, কিন্তু সম্মানজনকভাবে। "
                f"খুব আনুষ্ঠানিক বা খুব অনানুষ্ঠানিক হবেন না, মাঝামাঝি রাখুন।"
            )
        else:
            lang_name = "English"
            lang_instructions = (
                f"IMPORTANT: Respond in {lang_name} ({language}). The user has selected {lang_name} as their preferred language. "
                f"All your responses must be in {lang_name}."
            )
        
        # ID formatting instructions
        id_formatting_instructions = (
            "CRITICAL ID FORMATTING RULES:\n"
            "- ALL IDs must be in LOWERCASE format: user_id (e.g., 'u101'), order_id (e.g., 'o302'), "
            "ticket_id (e.g., 't602'), product_id (e.g., 'p001'), return order_id (e.g., 'o302').\n"
            "- When users mention IDs verbally (e.g., 'o302', 'O302', 'O 302'), ALWAYS convert to lowercase "
            "before calling tools (e.g., 'o302').\n"
            "- If STT or transcription provides capitalized IDs (e.g., 'O302'), convert them to lowercase "
            "immediately before using in tool calls.\n"
            "- Database lookups are case-sensitive and will fail if IDs are not lowercase.\n"
        )
        
        # Conversational response style instructions
        # Check if this is GreeterAgent (exclude from thank you branding)
        is_greeter = agent_name == "GreeterAgent"
        
        if language == "bn-BD":
            thank_you_branding = (
                "" if is_greeter else (
                    "\nTHANK YOU RESPONSE - CRITICAL:\n"
                    "- When the user says 'thank you', 'thanks', 'ধন্যবাদ', 'থ্যাংক ইউ', or similar gratitude expressions, "
                    "ALWAYS respond with: 'আপনাকে স্বাগতম। বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপের সাথে থাকার জন্য ধন্যবাদ।' "
                    "(Translation: 'You're welcome. Thank you for staying with Bangladesh number one e-commerce platform CartUp.')\n"
                    "- Keep it natural and warm, but always include the branding message.\n"
                )
            )
            
            # Scope limitation applies to ALL agents including GreeterAgent
            scope_limitation = (
                "\nSCOPE LIMITATION - CRITICAL:\n"
                "- You are a CartUp e-commerce customer service agent. You can ONLY help with:\n"
                "  * Order tracking, status, and modifications\n"
                "  * Support ticket creation and tracking\n"
                "  * Returns and refunds\n"
                "  * Product recommendations\n"
                "  * General CartUp platform questions\n"
                "- If the user asks for anything unrelated to e-commerce or CartUp (e.g., 'sing me a song', 'tell me a joke', "
                "'play music', 'tell a story', 'what's the weather', 'general knowledge questions', etc.), "
                "politely decline and redirect:\n"
                "  * Bengali: 'আমি দুঃখিত, আমি শুধুমাত্র কার্টআপের অর্ডার, টিকেট, রিটার্ন এবং পণ্য সম্পর্কিত সাহায্য করতে পারি। "
                "আপনি কীভাবে সাহায্য করতে পারি?' "
                "(Translation: 'I'm sorry, I can only help with CartUp orders, tickets, returns, and products. How can I help you?')\n"
                "- Be polite but firm - do not entertain non-e-commerce requests.\n"
            )
            
            conversational_instructions = (
                "RESPONSE STYLE - CRITICAL:\n"
                "- When presenting information from database queries or tool results, ALWAYS convert raw data into natural, conversational speech.\n"
                "- Do NOT read out structured data verbatim (e.g., don't say 'order_id: o302, status: Pending').\n"
                "- Instead, summarize and rephrase information as a friendly customer service agent would speak in Bangladesh Bengali.\n"
                "- For example, instead of 'Order o302 has status: Pending, items: [item1, item2], amount: 100', "
                "say 'আপনার o302 নম্বর অর্ডারটি এখনো প্রক্রিয়াধীন আছে। এতে [আইটেমের নাম] আছে এবং মোট ১০০ টাকা।'\n"
                "- Always use 'টাকা' or 'tk' (Taka) as the currency unit, not 'rupee' or other currencies.\n"
                "- Make responses sound natural and human-like, as if you're speaking directly to the customer in Bangladesh Bengali.\n"
                "- Focus on the key information the customer cares about, not technical details.\n"
                "- Avoid reading lists or dictionaries verbatim - summarize and present information conversationally in natural Bengali.\n"
                "- Use natural Bengali expressions: 'জি, অবশ্যই', 'আচ্ছা', 'ঠিক আছে', 'ধন্যবাদ' etc.\n"
                "- Speak in short, clear sentences. Avoid very long or complex sentences.\n"
                f"{thank_you_branding}"
                f"{scope_limitation}"
            )
        else:
            thank_you_branding = (
                "" if is_greeter else (
                    "\nTHANK YOU RESPONSE - CRITICAL:\n"
                    "- When the user says 'thank you', 'thanks', or similar gratitude expressions, "
                    "ALWAYS respond with: 'You're welcome. Thank you for staying with Bangladesh number one e-commerce platform CartUp.'\n"
                    "- Keep it natural and warm, but always include the branding message.\n"
                )
            )
            
            # Scope limitation applies to ALL agents including GreeterAgent
            scope_limitation = (
                "\nSCOPE LIMITATION - CRITICAL:\n"
                "- You are a CartUp e-commerce customer service agent. You can ONLY help with:\n"
                "  * Order tracking, status, and modifications\n"
                "  * Support ticket creation and tracking\n"
                "  * Returns and refunds\n"
                "  * Product recommendations\n"
                "  * General CartUp platform questions\n"
                "- If the user asks for anything unrelated to e-commerce or CartUp (e.g., 'sing me a song', 'tell me a joke', "
                "'play music', 'tell a story', 'what's the weather', 'general knowledge questions', etc.), "
                "politely decline and redirect:\n"
                "  * English: 'I'm sorry, I can only help with CartUp orders, tickets, returns, and products. How can I help you?'\n"
                "- Be polite but firm - do not entertain non-e-commerce requests.\n"
            )
            
            conversational_instructions = (
                "RESPONSE STYLE - CRITICAL:\n"
                "- When presenting information from database queries or tool results, ALWAYS convert raw data into natural, conversational speech.\n"
                "- Do NOT read out structured data verbatim (e.g., don't say 'order_id: o302, status: Pending').\n"
                "- Instead, summarize and rephrase information as a friendly customer service agent would speak.\n"
                "- For example, instead of 'Order o302 has status: Pending, items: [item1, item2], amount: 100', "
                "say 'Your order o302 is currently pending. It includes [item names] and the total is 100 tk.'\n"
                "- Always use 'tk' (Taka) as the currency unit, not 'rupee' or other currencies.\n"
                "- Make responses sound natural and human-like, as if you're speaking directly to the customer.\n"
                "- Focus on the key information the customer cares about, not technical details.\n"
                "- Avoid reading lists or dictionaries verbatim - summarize and present information conversationally.\n"
                f"{thank_you_branding}"
                f"{scope_limitation}"
            )
        
        chat_ctx.add_message(
            role="system",
            content=(
                f"You are {agent_name}. Current session summary:\n{userdata.summarize()}\n\n"
                f"{id_formatting_instructions}\n"
                f"{conversational_instructions}\n"
                f"{lang_instructions}"
            ),
        )
        
        await self.update_chat_ctx(chat_ctx)
        
        # Generate greeting for all agents
        if userdata.prev_agent is None:
            # Initial greeting for first agent (GreeterAgent)
            # GreeterAgent will use its own concise branding greeting
            if language == "bn-BD":
                await self.session.generate_reply(
                    instructions="Say concisely: 'স্বাগতম বাংলাদেশের নম্বর ওয়ান ই-কমার্স প্ল্যাটফর্ম কার্টআপে। আমি আপনাকে কীভাবে সাহায্য করতে পারি?' Keep it short and to the point. No extra explanations."
                )
            else:
                await self.session.generate_reply(
                    instructions="Say concisely: 'Welcome to Bangladesh number one e-commerce platform CartUp. How can I help you today?' Keep it short and to the point. No extra explanations."
                )
        else:
            # Default greeting for transferred agents (can be overridden)
            await self._generate_transfer_greeting()
    
    async def _generate_transfer_greeting(self) -> None:
        """No-op transfer greeting to avoid duplicate turns; the target agent's on_enter will greet."""
        return
    
    def _get_tts_for_language(self, language: str):
        """Helper method to get TTS instance for a given language."""
        return get_tts_for_language(language)
    
    async def _transfer_to_agent(
        self, name: str, context: RunContext_T
    ) -> Tuple[Agent, str]:
        """Transfer to another agent and return transfer tuple."""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent
        
        # Announce transfer before handing off to the target agent.
        return next_agent, f"Transferring to {name}."

