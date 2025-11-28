# agent.py
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# ...

import base64
import logging
import os
from datetime import date
import google.adk as adk
from typing import Optional


from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from fastapi import Request
from toolbox_core import ToolboxClient
from google.adk.tools.toolbox_toolset import ToolboxToolset
from .sub_agents.faith.faith_mental_agent import faith_mental_agent
from .sub_agents.plays.play_analysis_agent import play_analysis_agent
from .sub_agents.fitness.fitness_agent import fitness_agent
from .sub_agents.analytics.tools import get_database_settings as get_alloydb_database_settings
from .sub_agents.drills.drills_agent import drills_agent
from .tools import call_alloydb_agent
from .prompts import return_instructions_root

from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)



memory_service = VertexAiMemoryBankService(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    agent_engine_id=os.getenv("AGENT_ENGINE_ID")

)
session_service = VertexAiSessionService(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION"),
    agent_engine_id=os.getenv("AGENT_ENGINE_ID")
)


async def auto_save_to_memory_callback(callback_context):
    """Automatically save completed sessions to memory bank using default session user_id"""
    try:
        session_id = None

        # Extract session information from invocation context
        if hasattr(callback_context, "_invocation_context"):
            inv_ctx = callback_context._invocation_context

            # Extract session ID
            if hasattr(inv_ctx, "session") and hasattr(inv_ctx.session, "id"):
                session_id = inv_ctx.session.id

        # Get the session from the invocation context
        session = callback_context._invocation_context.session

        if not session_id:
            return

        # Initialize memory service
        agent_engine_id = os.getenv("AGENT_ENGINE_ID")
        if not agent_engine_id:
            return

        memory_service = VertexAiMemoryBankService(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
            agent_engine_id=agent_engine_id,
        )

        # Check if session has meaningful content
        has_content = False
        content_count = 0

        if hasattr(session, "events") and session.events:
            content_count = len(session.events)
            has_content = content_count >= 2  # At least user message + agent response
        elif hasattr(session, "contents") and session.contents:
            content_count = len(session.contents)
            has_content = content_count >= 2

        if not has_content:
            return

        await memory_service.add_session_to_memory(session)
        print(f"🧠 Session auto-saved to memory bank")

    except Exception as e:
        print(f"⚠️ Error auto-saving to memory: {e}")

async def search_memory( query: Optional[str] = None) -> list:
    """
    Search Vertex AI memory bank for relevant information about the user's learning progress.
    The agent is instructed to pass the student's user_name as the query,
    as a temp. workaround to: https://github.com/google/adk-web/issues/49
    """
    app_name = "ai_agent"
    user_id = "user"  # hardcoding this, searching by user's first name
    print(
        f"🔍 SEARCHING MEMORY BANK for app_name='{app_name}', user_id='{user_id}', query='{query}'..."
    )

    memory_bank_service = VertexAiMemoryBankService(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        agent_engine_id=os.getenv("AGENT_ENGINE_ID"),
    )
    try:
        search_results = await memory_bank_service.search_memory(
            app_name=app_name,
            user_id=user_id,
            query=query

        
        )
        print(f"✅ SearchMemoryResponse: ")
        print(search_results)
        return search_results
    except Exception as e:
        print(f"❌ Error searching memory: {e}")
        return []


# Load AlloyDB settings once
_database_settings = get_alloydb_database_settings()

def load_database_settings_in_context(callback_context: CallbackContext):
    """Load database settings into the callback context."""
    if "database_settings" not in callback_context.state:
        callback_context.state["database_settings"] = _database_settings



# --- Sub-agents list ---
all_agents = [faith_mental_agent,drills_agent, play_analysis_agent, fitness_agent]

def get_root_agent() -> LlmAgent:
    """Return the top-level root agent with sub-agents and AlloyDB tools."""
    agent = LlmAgent(
        model=os.getenv("ROOT_AGENT_MODEL", "gemini-2.5-flash"),
        name="root_agent",

        instruction=return_instructions_root() ,
        sub_agents=all_agents,           # Register true sub-agents
        tools=[call_alloydb_agent,search_memory],      # AlloyDB tool
        before_agent_callback=load_database_settings_in_context,
        after_agent_callback= auto_save_to_memory_callback,
        generate_content_config=types.GenerateContentConfig(temperature=0.01),
    )
    return agent

root_agent = get_root_agent()
runner = adk.Runner(
    agent=root_agent,
    app_name="ai_agent",
    session_service=session_service,
    memory_service=memory_service
)
