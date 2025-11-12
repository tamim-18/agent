"""
Main entry point for CartUp e-commerce voice agent
"""

# Load environment variables FIRST before any imports that need them
from dotenv import load_dotenv
load_dotenv(".env")

import logging
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.voice import AgentSession
from livekit.plugins import google, openai, silero, noise_cancellation
from livekit.agents import RoomInputOptions
from .database.db import init_database
from .session.user_data import UserData
from .agents.greeter_agent import GreeterAgent
from .agents.order_agent import OrderAgent
from .agents.ticket_agent import TicketAgent
from .agents.return_agent import ReturnAgent
from .agents.recommend_agent import RecommendAgent

logger = logging.getLogger("cartup-agent")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    """Entry point for the CartUp voice agent."""
    logger.info(f"CartUp agent started in room: {ctx.room.name}")
    
    # Extract language from room name
    # Room name pattern: "voice_assistant_room_{language}_{random}"
    room_name_parts = ctx.room.name.split('_')
    language = "en-IN"  # Default fallback
    
    # Try to extract language from room name
    if len(room_name_parts) >= 4 and room_name_parts[-2] in ["en-IN", "bn-BD"]:
        language = room_name_parts[-2]
    elif len(room_name_parts) >= 3:
        # Fallback: check if any part matches language codes
        for part in room_name_parts:
            if part in ["en-IN", "bn-BD"]:
                language = part
                break
    
    logger.info(f"Detected language from room name: {language}")
    
    # Initialize database with sample data
    init_database()
    logger.info("Database initialized")
    
    # Create session state
    userdata = UserData()
    userdata.language = language  # Set language upfront
    
    # Instantiate all agents
    userdata.agents.update({
        "greeter": GreeterAgent(),
        "order": OrderAgent(),
        "ticket": TicketAgent(),
        "returns": ReturnAgent(),
        "recommend": RecommendAgent(),
    })
    logger.info("All agents instantiated")
    
    # Configure STT based on selected language
    if language == "bn-BD":
        # Bengali STT configuration
        stt_config = google.STT(
            model="chirp_2",  # Bengali model
            location="asia-northeast1",  # Required location for chirp_2 with Bengali support
            languages=["bn-BD"],  # Bangladesh Bengali
            detect_language=False,  # Disable auto-detection since we know the language
        )
        logger.info("Configured STT for Bengali (bn-BD)")
    else:
        # English STT configuration
        stt_config = google.STT(
            model="chirp_2",  # English model (verify available models)
            location="asia-northeast1",  # May need different location for English
            languages=["en-IN"],  # English (India)
            detect_language=False,  # Disable auto-detection
        )
        logger.info("Configured STT for English (en-IN)")
    
    # Configure TTS based on selected language (same approach as STT)
    from .config import get_tts_for_language
    
    if language == "bn-BD":
        # Bengali TTS configuration - using bn-IN voices with Bangladesh accent via LLM instructions
        tts_config = get_tts_for_language("bn-BD", gender="female")  # Default to female voice (bn-IN-Chirp3-HD-Despina)
        logger.info("Configured TTS for Bengali (bn-IN voices) - Bangladesh accent maintained via LLM")
    else:
        # English TTS configuration
        tts_config = get_tts_for_language("en-IN")
        logger.info("Configured TTS for English (en-IN)")
    
    # Configure voice pipeline
    session = AgentSession[UserData](
        userdata=userdata,
        stt=stt_config,
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=tts_config,  # Language-aware TTS configuration
        vad=silero.VAD.load(),
        max_tool_steps=5,
    )
    
    # Start session with greeter agent
    await session.start(
        agent=userdata.agents["greeter"],
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    logger.info(f"Session started with greeter agent (Language: {language})")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

