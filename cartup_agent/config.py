"""
Configuration module for CartUp voice agent
Contains voice IDs, model configuration, and agent settings
"""

from livekit.plugins import google, silero

# Voice configuration for different agents
# Note: Using Google TTS with en-IN-Chirp-HD-F voice (Indian English, Chirp HD, Female)
# Can be customized per agent if needed
VOICES = {
    "greeter": "female",
    "order": "female",
    "ticket": "female",
    "returns": "female",
    "recommend": "female",
}

# Model configuration matching livekit_basic_agent.py
def get_voice_pipeline():
    """Returns configured voice pipeline components."""
    return {
        "stt": google.STT(),
        "llm": google.LLM(model="gemini-2.0-flash"),
        "tts": google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
        "vad": silero.VAD.load(),
    }

# Agent-specific configurations
AGENT_CONFIG = {
    "max_tool_steps": 5,
    "parallel_tool_calls": False,
}

