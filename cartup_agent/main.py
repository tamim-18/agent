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
    
    # Configure voice pipeline (matching livekit_basic_agent.py)
    session = AgentSession[UserData](
        userdata=userdata,
        stt=google.STT(),
        llm=google.LLM(model="gemini-2.0-flash"),
        tts=google.TTS(voice_name="en-IN-Chirp-HD-F", language="en-IN"),
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

