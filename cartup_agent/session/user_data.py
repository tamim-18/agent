"""
Session state management for CartUp voice agent
Contains UserData dataclass and type aliases
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
import yaml

from livekit.agents.voice import Agent, RunContext


@dataclass
class UserData:
    """Session state that persists across agent transfers."""
    
    # User identification
    user_id: Optional[str] = None
    
    # Context tracking (frequently referenced entities)
    current_order_id: Optional[str] = None
    current_ticket_id: Optional[str] = None
    current_product_id: Optional[str] = None
    
    # Conversation state
    last_intent: Optional[str] = None
    
    # Language preference
    language: Optional[str] = None  # "en-IN" (English) or "bn-BD" (Bangladesh Bengali)
    
    # Agent management
    agents: Dict[str, Agent] = field(default_factory=dict)
    prev_agent: Optional[Agent] = None
    
    def summarize(self) -> str:
        """Generate YAML summary of current session state for LLM context."""
        data = {
            "user_id": self.user_id or "unknown",
            "current_order_id": self.current_order_id or "none",
            "current_ticket_id": self.current_ticket_id or "none",
            "current_product_id": self.current_product_id or "none",
            "last_intent": self.last_intent or "none",
            "language": self.language or "en-IN",  # Default to English if not set (bn-BD for Bangladesh Bengali)
        }
        return yaml.dump(data)


# Type alias for RunContext with UserData
RunContext_T = RunContext[UserData]

