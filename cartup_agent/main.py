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
from livekit.plugins import google, silero, noise_cancellation
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
    
    # Initialize database with sample data
    init_database()
    logger.info("Database initialized")
    
    # Create session state
    userdata = UserData()
    
    # Instantiate all agents
    userdata.agents.update({
        "greeter": GreeterAgent(),
        "order": OrderAgent(),
        "ticket": TicketAgent(),
        "returns": ReturnAgent(),
        "recommend": RecommendAgent(),
    })
    logger.info("All agents instantiated")
    
    # Configure voice pipeline
    # STT is configured to support both English and Bengali using the 'chirp_2' model
    # CRITICAL: Multiple language recognition (specifying both en-IN and bn-IN) is ONLY
    # available in locations: 'eu', 'global', or 'us'. Using 'global' location.
    # Note: If chirp_2 is not available in 'global', we may need to use a different approach.
    # TTS will be dynamically configured per agent based on user's language preference.
    session = AgentSession[UserData](
        userdata=userdata,
        stt=google.STT(
            # Use chirp_2 with Bengali in asia-northeast1 (where it's available)
            # Note: Multiple languages not supported in asia-northeast1, so using Bengali only
            # The greeter will handle English responses initially via LLM
            model="chirp_2",  # chirp_2 model supports Bengali (bn-BD for Bangladesh)
            location="asia-northeast1",  # Required location for chirp_2 with Bengali support
            languages=["bn-BD"],  # Bangladesh Bengali - primary language for STT
            detect_language=True,  # Enable auto-detection (may help with English too)
        ),
        llm=google.LLM(model="gemini-2.0-flash"),
        tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),  # Default, will be overridden per agent
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
    
    logger.info("Session started with greeter agent")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

