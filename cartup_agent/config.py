"""
Configuration module for CartUp voice agent
Contains voice IDs, model configuration, and agent settings
"""

from livekit.plugins import google, openai, silero

# Supported languages
SUPPORTED_LANGUAGES = ["en-IN", "bn-BD"]  # bn-BD for Bangladesh Bengali accent

# TTS voice configuration per language
ENGLISH_TTS_VOICE = "en-IN-Chirp-HD-F"

# Bengali TTS voices - using selected premium voices from Google Cloud TTS
# Selected voices from Google Cloud TTS Premium models (Bengali India):
# FEMALE: Despina (bn-IN-Chirp3-HD-Despina)
# MALE: Alnilam, Rasalgethi (bn-IN-Chirp3-HD-Alnilam, bn-IN-Chirp3-HD-Rasalgethi)
# Note: Using bn-IN voices but maintaining Bangladesh Bengali accent via LLM instructions
# Default female voice for general use
BENGALI_TTS_VOICE_FEMALE = "bn-IN-Chirp3-HD-Despina"  # Bengali India - Female
# Default male voice for general use
BENGALI_TTS_VOICE_MALE = "bn-IN-Chirp3-HD-Rasalgethi"  # Bengali India - Male
# Alternative male voice
BENGALI_TTS_VOICE_MALE_ALT = "bn-IN-Chirp3-HD-Alnilam"  # Bengali India - Male (Alternative)
# Default voice (female)
BENGALI_TTS_VOICE = BENGALI_TTS_VOICE_FEMALE  # Default to female voice

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
        "tts": google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN", speaking_rate=1.2),
        "vad": silero.VAD.load(),
    }

# Agent-specific configurations
AGENT_CONFIG = {
    "max_tool_steps": 5,
    "parallel_tool_calls": False,
}


def get_tts_for_language(language: str, voice_name: str = None, gender: str = "female", speaking_rate: float = 1.2):
    """
    Returns appropriate TTS instance based on language preference.
    
    Args:
        language: Language code ("en-IN" or "bn-BD" for Bangladesh Bengali)
        voice_name: Optional specific voice name to use (overrides default and gender)
        gender: Gender preference ("male" or "female") - only used for Bengali if voice_name not provided
        speaking_rate: Speaking rate multiplier (0.25 to 4.0, default 1.2 for 1.2x speed)
    
    Returns:
        Google TTS instance configured for the specified language
    """
    if language == "bn-BD":
        if voice_name:
            voice = voice_name
        elif gender == "male":
            voice = BENGALI_TTS_VOICE_MALE
        else:
            voice = BENGALI_TTS_VOICE_FEMALE
        # Use bn-IN language code for TTS (voices are bn-IN), but accent comes from LLM instructions
        return google.TTS(voice_name=voice, language="bn-IN", speaking_rate=speaking_rate)
    else:
        # Default to English
        voice = voice_name or ENGLISH_TTS_VOICE
        return google.TTS(voice_name=voice, language="en-IN", speaking_rate=speaking_rate)


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

