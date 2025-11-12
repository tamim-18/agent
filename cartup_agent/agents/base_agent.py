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
            ).truncate(max_items=20)
            
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
                f"All your responses must be in Bangladesh Bengali with authentic Bangladesh accent."
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
        
        chat_ctx.add_message(
            role="system",
            content=(
                f"You are {agent_name}. Current session summary:\n{userdata.summarize()}\n\n"
                f"{id_formatting_instructions}\n"
                f"{lang_instructions}"
            ),
        )
        
        await self.update_chat_ctx(chat_ctx)
        
        # Generate greeting for all agents
        if userdata.prev_agent is None:
            # Initial greeting for first agent (GreeterAgent)
            # GreeterAgent will handle language selection via its instructions
            await self.session.generate_reply(
                instructions="Greet the user warmly. First check if language is set. If not, offer language selection between English and Bengali. Then ask how you can help."
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

