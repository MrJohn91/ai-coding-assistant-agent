"""
FastAPI endpoints using Pydantic AI agent (refactored version).

This module demonstrates the Pydantic AI + Mem0 integration
following patterns from the research phase.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from src.agent.dependencies import SalesBikeAgentDeps
from src.agent.pydantic_agent import sales_agent, save_conversation_memory
from src.api.models import MessageRequest, MessageResponse
from pydantic_ai import RunContext

logger = logging.getLogger(__name__)

# Create router for Pydantic AI endpoints
router = APIRouter(prefix="/api/v2", tags=["Pydantic AI Agent"])


@router.post(
    "/conversations/{session_id}/messages",
    response_model=MessageResponse,
    summary="Send message (Pydantic AI version)"
)
async def send_message_pydantic(
    session_id: str,
    request: MessageRequest,
    fastapi_request: Request
):
    """
    Send a message using Pydantic AI agent with Mem0 memory.

    This endpoint demonstrates the refactored approach:
    - Pydantic AI agent with dependency injection
    - Mem0 conversation memory
    - Archon RAG for product/FAQ search

    Args:
        session_id: Conversation session ID
        request: Message request with user message
        fastapi_request: FastAPI request for accessing app.state

    Returns:
        Agent response with optional product recommendations

    Raises:
        HTTPException: If session not found or agent fails
    """
    app = fastapi_request.app

    # Get or create session
    session = app.state.orchestrator.session_store.get_session(session_id)
    if not session:
        # Auto-create session if it doesn't exist (for v2 endpoints)
        # Note: We create a new session but the session_id in URL might not match
        # For proper usage, client should call /api/v1/conversations first
        session = app.state.orchestrator.session_store.create_session()
        # Store with the requested session_id for consistency
        session.id = session_id
        app.state.orchestrator.session_store._sessions[session_id] = session
        logger.info(f"Auto-created new session: {session_id}")

    logger.info(f"[Pydantic AI] Processing message in session {session_id}: {request.message}")

    try:
        # Build dependencies for Pydantic AI agent
        # Following the pattern from our research
        deps = SalesBikeAgentDeps(
            mcp_client=app.state.mcp_client if hasattr(app.state, 'mcp_client') else None,
            memory_client=app.state.memory_client if hasattr(app.state, 'memory_client') else None,
            crm_client=app.state.orchestrator.crm_client,
            session_store=app.state.orchestrator.session_store,
            http_client=app.state.http_client if hasattr(app.state, 'http_client') else None,
            product_store=app.state.product_store if hasattr(app.state, 'product_store') else None,
            faq_store=app.state.faq_store if hasattr(app.state, 'faq_store') else None,
            llm=app.state.llm if hasattr(app.state, 'llm') else None
        )

        # Get user_id from session context if available
        user_id = getattr(session.context, 'customer_email', None) or session_id

        # Run Pydantic AI agent
        # Pattern: agent.run(prompt, deps=deps)
        result = await sales_agent.run(
            request.message,
            deps=deps
        )

        # Extract response
        response_text = result.data if hasattr(result, 'data') else str(result)

        # Add messages to session history
        session.add_message("user", request.message)
        session.add_message("assistant", response_text)
        app.state.orchestrator.session_store.update_session(session)

        # Save conversation to Mem0 for future recall
        # Using the Mem0 pattern from our research
        if deps.memory_client and user_id:
            logger.info(f"Saving conversation memory for user: {user_id}")
            try:
                # Call Mem0 directly instead of through the tool
                deps.memory_client.add(
                    messages=[
                        {"role": "user", "content": request.message},
                        {"role": "assistant", "content": response_text}
                    ],
                    user_id=user_id,
                    output_format="v1.0"
                )
                logger.info(f"Successfully saved conversation to Mem0 for user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to save to Mem0: {e}", exc_info=True)

        return MessageResponse(
            session_id=session_id,
            response=response_text,
            products=None,  # TODO: Extract from agent tool calls
            lead_created=False  # TODO: Detect from agent actions
        )

    except Exception as e:
        logger.error(f"Error in Pydantic AI agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check for Pydantic AI agent"
)
async def health_check_pydantic(fastapi_request: Request):
    """
    Check health of Pydantic AI agent and dependencies.

    Returns:
        Health status with component availability
    """
    app = fastapi_request.app

    return {
        "status": "ok",
        "agent": "pydantic_ai",
        "components": {
            "mcp_client": hasattr(app.state, 'mcp_client') and app.state.mcp_client is not None,
            "memory_client": hasattr(app.state, 'memory_client') and app.state.memory_client is not None,
            "http_client": hasattr(app.state, 'http_client') and app.state.http_client is not None,
            "orchestrator": hasattr(app.state, 'orchestrator') and app.state.orchestrator is not None
        }
    }
