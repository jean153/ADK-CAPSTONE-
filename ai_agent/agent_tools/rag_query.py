import logging
from vertexai import rag
from google.adk.tools.tool_context import ToolContext
from .config import DEFAULT_DISTANCE_THRESHOLD, DEFAULT_TOP_K

# Map agent names to their respective corpus resource names
AGENT_CORPUS_RESOURCES = {
    "fitness_agent":"projects/gen-lang-client-0264313586/locations/us-east1/ragCorpora/1152921504606846976"
    ,"play_analysis_agent": "projects/gen-lang-client-0264313586/locations/us-east1/ragCorpora/7454583283205013504",
    # Add more agents here
}

def preloaded_rag_query(query: str, tool_context: ToolContext, agent_name: str = "fitness_agent") -> dict:
    """
    Query the preloaded Vertex AI RAG corpus with a user question.
    Each agent can call its respective corpus using `agent_name`.
    """
    try:
        # Select corpus for this agent
        corpus_resource_name = AGENT_CORPUS_RESOURCES.get(agent_name)
        if not corpus_resource_name:
            raise ValueError(f"No corpus configured for agent: {agent_name}")

        # Configure retrieval parameters
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=DEFAULT_TOP_K,
            filter=rag.Filter(vector_distance_threshold=DEFAULT_DISTANCE_THRESHOLD),
        )

        # Perform the query
        response = rag.retrieval_query(
            rag_resources=[rag.RagResource(rag_corpus=corpus_resource_name)],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )

        # Process the response into a usable format
        results = []
        if hasattr(response, "contexts") and response.contexts:
            for ctx_group in response.contexts.contexts:
                results.append({
                    "source_uri": getattr(ctx_group, "source_uri", ""),
                    "source_name": getattr(ctx_group, "source_display_name", ""),
                    "text": getattr(ctx_group, "text", ""),
                    "score": getattr(ctx_group, "score", 0.0),
                })

        if not results:
            return {
                "status": "warning",
                "message": f"No results found for query: '{query}'",
                "query": query,
                "results": [],
                "results_count": 0,
            }

        return {
            "status": "success",
            "message": f"Successfully queried preloaded corpus for {agent_name}",
            "query": query,
            "results": results,
            "results_count": len(results),
        }

    except Exception as e:
        error_msg = f"Error querying preloaded corpus: {str(e)}"
        logging.error(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "query": query,
            "results": [],
            "results_count": 0,
        }
