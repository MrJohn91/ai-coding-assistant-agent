"""FastAPI application for Sales Bike Agent."""

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from mem0 import MemoryClient

from src.agent.orchestrator import AgentOrchestrator
from src.agent.session import SessionStore
from src.api.middleware import LoggingMiddleware, error_handler
from src.api.models import (
    ConversationCreateResponse,
    ConversationHistoryResponse,
    HealthResponse,
    MessageRequest,
    MessageResponse,
)
from src.config import settings
from src.crm.client import CRMClient
from src.llm.factory import get_llm_provider
from src.vector_store.embedder import get_embedder
from src.vector_store.faiss_store import FAQVectorStore, ProductVectorStore

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global instances (initialized in lifespan)
session_store: SessionStore = None
orchestrator: AgentOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown.

    Args:
        app: FastAPI application
    """
    global session_store, orchestrator

    # Startup
    logger.info("Starting Sales Bike Agent API...")

    try:
        # Initialize embedder and LLM
        logger.info("Loading embedder and LLM...")
        embedder = get_embedder(settings.llm_provider)
        llm = get_llm_provider(settings.llm_provider)

        # Load vector stores
        logger.info(f"Loading vector stores from {settings.faiss_index_path}...")
        product_store = ProductVectorStore(embedder)
        faq_store = FAQVectorStore(embedder)

        # Check if indices exist
        if settings.faiss_index_path.exists():
            product_store.load(settings.faiss_index_path)
            faq_store.load(settings.faiss_index_path)
            logger.info("Vector stores loaded successfully")
        else:
            logger.warning(
                f"Vector store indices not found at {settings.faiss_index_path}. "
                "Please run 'python -m src.data.setup_vector_store' first."
            )

        # Initialize session store
        session_store = SessionStore(ttl_minutes=settings.session_ttl_minutes)

        # Initialize CRM client
        crm_client = CRMClient()

        # Initialize Mem0 client (following Mem0 docs pattern)
        # Reference: Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)
        memory_client = None
        if settings.mem0_api_key:
            logger.info("Initializing Mem0 memory client...")
            memory_client = MemoryClient(api_key=settings.mem0_api_key)
            logger.info("Mem0 client initialized successfully")
        else:
            logger.warning("Mem0 API key not found. Memory features will be disabled.")

        # Initialize HTTP client for async requests
        http_client = httpx.AsyncClient()

        # Initialize MCP client for Archon (placeholder)
        # In production, this would connect to running Archon MCP server
        # For now, we'll use None and the Pydantic AI agent will handle gracefully
        mcp_client = None
        logger.warning("MCP client not initialized. Archon RAG features will be limited.")
        # TODO: Add actual MCP client initialization when deploying with Archon

        # Store clients and vector stores in app.state for later use
        app.state.memory_client = memory_client
        app.state.http_client = http_client
        app.state.mcp_client = mcp_client
        app.state.product_store = product_store
        app.state.faq_store = faq_store
        app.state.llm = llm

        # Initialize orchestrator (used by legacy v1 endpoints)
        # NOTE: v2 endpoints use Pydantic AI agent directly
        try:
            orchestrator = AgentOrchestrator(
                session_store=session_store,
                product_store=product_store,
                faq_store=faq_store,
                llm=llm,
                crm_client=crm_client,
            )
            app.state.orchestrator = orchestrator
            logger.info("Legacy orchestrator initialized successfully")
        except TypeError as e:
            logger.warning(f"Could not initialize legacy orchestrator: {e}. V1 endpoints will not work.")
            # Create a minimal orchestrator object for v2 endpoints that need session_store and crm_client
            class MinimalOrchestrator:
                def __init__(self, session_store, crm_client):
                    self.session_store = session_store
                    self.crm_client = crm_client

            orchestrator = MinimalOrchestrator(session_store=session_store, crm_client=crm_client)
            app.state.orchestrator = orchestrator
            logger.info("Minimal orchestrator created for v2 endpoints")

        logger.info("Sales Bike Agent API started successfully")

    except Exception as e:
        logger.error(f"Failed to start API: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Sales Bike Agent API...")

    # Close HTTP client
    if hasattr(app.state, 'http_client') and app.state.http_client:
        await app.state.http_client.aclose()
        logger.info("HTTP client closed")


# Create FastAPI app
app = FastAPI(
    title="Sales Bike Agent API",
    description="AI-powered sales agent for bike shop",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add exception handler
app.add_exception_handler(Exception, error_handler)

# Include Pydantic AI router (v2 endpoints)
from src.api.pydantic_endpoints import router as pydantic_router
app.include_router(pydantic_router)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(status="ok")


@app.post(
    "/api/v1/conversations",
    response_model=ConversationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Conversations"],
)
async def create_conversation():
    """Create a new conversation session.

    Returns:
        New session ID and welcome message
    """
    session = session_store.create_session()

    logger.info(f"Created new conversation: {session.id}")

    return ConversationCreateResponse(
        session_id=session.id,
        message="Hello! I'm your bike shop assistant. What type of bike are you looking for today?",
    )


@app.post(
    "/api/v1/conversations/{session_id}/messages",
    response_model=MessageResponse,
    tags=["Conversations"],
)
async def send_message(session_id: str, request: MessageRequest):
    """Send a message in an existing conversation.

    Args:
        session_id: Conversation session ID
        request: Message request

    Returns:
        Agent response

    Raises:
        HTTPException: If session not found
    """
    # Check if session exists
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {session_id} not found or expired",
        )

    logger.info(f"Received message in session {session_id}: {request.message}")

    # Process message with orchestrator
    response_text, products, lead_created = await orchestrator.process_message(
        session_id, request.message
    )

    return MessageResponse(
        session_id=session_id,
        response=response_text,
        products=products,
        lead_created=lead_created,
    )


@app.get(
    "/api/v1/conversations/{session_id}",
    response_model=ConversationHistoryResponse,
    tags=["Conversations"],
)
async def get_conversation(session_id: str):
    """Get conversation history.

    Args:
        session_id: Conversation session ID

    Returns:
        Conversation history

    Raises:
        HTTPException: If session not found
    """
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {session_id} not found or expired",
        )

    return ConversationHistoryResponse(
        session_id=session_id,
        messages=session.messages,
        state=session.state.value,
        created_at=session.created_at.isoformat(),
    )


@app.delete(
    "/api/v1/conversations/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Conversations"],
)
async def delete_conversation(session_id: str):
    """Delete a conversation session.

    Args:
        session_id: Conversation session ID

    Raises:
        HTTPException: If session not found
    """
    success = session_store.delete_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation {session_id} not found",
        )

    logger.info(f"Deleted conversation: {session_id}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
