"""
Configuration module for CartUp voice agent
Contains voice IDs, model configuration, and agent settings
"""

from livekit.plugins import google, openai, silero

# Supported languages
SUPPORTED_LANGUAGES = ["en-IN", "bn-BD"]  # bn-BD for Bangladesh Bengali accent

# TTS voice configuration per language
ENGLISH_TTS_VOICE = "en-IN-Chirp-HD-F"

# Bengali TTS voices for Bangladesh (bn-BD) - try different ones for better accent
# Note: Using Bangladesh Bengali (bn-BD) for authentic Bangladesh accent
# Available options include (same voice names, but use bn-BD language code):
# FEMALE: Achernar, Aoede, Autonoe, Callirrhoe, Despina, Erinome, Gacrux, Kore, Laomedeia, Leda, Pulcherrima, Sulafat, Vindemiatrix, Zephyr
# MALE: Achird, Algenib, Algieba, Alnilam, Charon, Enceladus, Fenrir, Iapetus, Orus, Puck, Rasalgethi, Sadachbia, Sadaltager, Schedar, Umbriel, Zubenelgenubi
# Currently using: Achernar (FEMALE) with bn-BD for Bangladesh accent
BENGALI_TTS_VOICE = "bn-BD-Chirp3-HD-Achernar"  # Bangladesh Bengali accent

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
        "llm": openai.LLM(model="gpt-4o-mini"),
        "tts": google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
        "vad": silero.VAD.load(),
    }

# Agent-specific configurations
AGENT_CONFIG = {
    "max_tool_steps": 5,
    "parallel_tool_calls": False,
}


def get_tts_for_language(language: str, voice_name: str = None):
    """
    Returns appropriate TTS instance based on language preference.
    
    Args:
        language: Language code ("en-IN" or "bn-BD" for Bangladesh Bengali)
        voice_name: Optional specific voice name to use (overrides default)
    
    Returns:
        Google TTS instance configured for the specified language
    """
    if language == "bn-BD":
        voice = voice_name or BENGALI_TTS_VOICE
        return google.TTS(voice_name=voice, language="bn-BD")
    else:
        # Default to English
        voice = voice_name or ENGLISH_TTS_VOICE
        return google.TTS(voice_name=voice, language="en-IN")


# Bengali voice options for Bangladesh (bn-BD) - for easy testing
# Note: Use bn-BD language code for Bangladesh accent
BENGALI_VOICES = {
    "female": [
        "bn-BD-Chirp3-HD-Achernar",      # Currently using
        "bn-BD-Chirp3-HD-Aoede",
        "bn-BD-Chirp3-HD-Autonoe",
        "bn-BD-Chirp3-HD-Callirrhoe",
        "bn-BD-Chirp3-HD-Despina",
        "bn-BD-Chirp3-HD-Erinome",
        "bn-BD-Chirp3-HD-Gacrux",
        "bn-BD-Chirp3-HD-Kore",
        "bn-BD-Chirp3-HD-Laomedeia",
        "bn-BD-Chirp3-HD-Leda",
        "bn-BD-Chirp3-HD-Pulcherrima",
        "bn-BD-Chirp3-HD-Sulafat",
        "bn-BD-Chirp3-HD-Vindemiatrix",
        "bn-BD-Chirp3-HD-Zephyr",
    ],
    "male": [
        "bn-BD-Chirp3-HD-Achird",
        "bn-BD-Chirp3-HD-Algenib",
        "bn-BD-Chirp3-HD-Algieba",
        "bn-BD-Chirp3-HD-Alnilam",
        "bn-BD-Chirp3-HD-Charon",
        "bn-BD-Chirp3-HD-Enceladus",
        "bn-BD-Chirp3-HD-Fenrir",
        "bn-BD-Chirp3-HD-Iapetus",
        "bn-BD-Chirp3-HD-Orus",
        "bn-BD-Chirp3-HD-Puck",
        "bn-BD-Chirp3-HD-Rasalgethi",
        "bn-BD-Chirp3-HD-Sadachbia",
        "bn-BD-Chirp3-HD-Sadaltager",
        "bn-BD-Chirp3-HD-Schedar",
        "bn-BD-Chirp3-HD-Umbriel",
        "bn-BD-Chirp3-HD-Zubenelgenubi",
    ]
}

