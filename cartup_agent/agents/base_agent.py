"""
Base agent class with shared functionality for all CartUp agents
Handles context handoff and agent transfers
"""

import logging
from typing import Tuple
from livekit.agents.voice import Agent

from ..session.user_data import UserData, RunContext_T

logger = logging.getLogger("cartup-agent")


class BaseAgent(Agent):
    """Base class for all CartUp agents with shared functionality."""
    
    async def on_enter(self) -> None:
        """Called when agent becomes active. Handles context handoff."""
        agent_name = self.__class__.__name__
        logger.info(f"Entering {agent_name}")
        
        userdata: UserData = self.session.userdata
        chat_ctx = self.chat_ctx.copy()
        
        # Copy truncated chat history from previous agent
        if isinstance(userdata.prev_agent, Agent):
            truncated_chat_ctx = userdata.prev_agent.chat_ctx.copy(
                exclude_instructions=True,
                exclude_function_call=False
            ).truncate(max_items=6)
            
            existing_ids = {item.id for item in chat_ctx.items}
            items_copy = [
                item for item in truncated_chat_ctx.items
                if item.id not in existing_ids
            ]
            chat_ctx.items.extend(items_copy)
        
        # Inject live summary for fast grounding
        chat_ctx.add_message(
            role="system",
            content=f"You are {agent_name}. Current session summary:\n{userdata.summarize()}",
        )
        
        await self.update_chat_ctx(chat_ctx)
        
        # Generate greeting for all agents
        if userdata.prev_agent is None:
            # Initial greeting for first agent (GreeterAgent)
            await self.session.generate_reply(
                instructions="Greet the user warmly and ask how you can help."
            )
        else:
            # Default greeting for transferred agents (can be overridden)
            await self._generate_transfer_greeting()
    
    async def _generate_transfer_greeting(self) -> None:
        """Generate a greeting when agent is transferred. Override in subclasses for custom greetings."""
        await self.session.generate_reply(
            instructions="Greet the user briefly and let them know you're here to help with their request. Be friendly and concise."
        )
    
    async def _transfer_to_agent(
        self, name: str, context: RunContext_T
    ) -> Tuple[Agent, str]:
        """Transfer to another agent and return transfer tuple."""
        userdata = context.userdata
        current_agent = context.session.current_agent
        next_agent = userdata.agents[name]
        userdata.prev_agent = current_agent
        
        return next_agent, f"Transferring to {name}."

