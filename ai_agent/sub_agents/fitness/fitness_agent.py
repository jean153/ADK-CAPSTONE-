from google.adk.agents import Agent
from ...agent_tools.rag_query import preloaded_rag_query
from . import prompt

from .tools import (
    create_event,
    delete_event,
    edit_event,
    get_current_time,
    list_events,
    get_location 
)
import os
from typing import Optional
from google.adk.memory import VertexAiMemoryBankService


FITNESS_AGENT_NAME = "fitness_agent"

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




def fitness_rag_query(query: str, tool_context=None):
    """
    Simple ADK-facing wrapper.
    Delegates to the preloaded RAG query function directly.
    """
    return preloaded_rag_query(query, tool_context, agent_name=FITNESS_AGENT_NAME)

fitness_agent = Agent(
    model='gemini-2.5-flash',
    name='fitness_agent',
    description='Provides basketball-specific nutrition and fitness advice',
    tools=[fitness_rag_query,
           list_events,
           create_event,
           edit_event,
           delete_event,
           get_location,
           search_memory
           ],  # ADK will call this directly
    instruction=prompt.FITNESS_PROMPT,
    after_agent_callback= auto_save_to_memory_callback
)
