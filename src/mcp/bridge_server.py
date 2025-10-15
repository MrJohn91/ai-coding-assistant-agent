"""
MCP Bridge Server - HTTP wrapper for Archon MCP tools.

PURPOSE:
This bridge allows your FastAPI app to access Archon's knowledge base.

CURRENT STATUS:
- ✅ HTTP server skeleton ready
- ⚠️ Needs connection to standalone Archon MCP server
- 💡 For development: Use local FAISS stores (already working!)

WHY YOU NEED THIS:
FastAPI runs as separate process and can't access Claude Code's MCP tools directly.
This bridge converts HTTP requests → MCP calls → Archon knowledge base.

WHEN TO USE:
- Production deployments
- Large/frequently changing datasets
- Multiple services need Archon access

FOR NOW:
Continue using local FAISS stores in your agent. See README.md for details.

PRODUCTION SETUP (FUTURE):
1. Deploy Archon MCP as standalone server
2. Update this file to connect to it (replace TODO sections)
3. Start bridge: python -m src.mcp.bridge_server
4. Enable in main.py: mcp_client = ArchonMCPClient("http://localhost:8001")
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Archon MCP Bridge",
    description="HTTP bridge to Archon MCP server for RAG operations",
    version="1.0.0",
)


# Request/Response models
class RAGSearchRequest(BaseModel):
    """Request model for RAG search."""
    query: str
    source_id: str
    match_count: int = 5
    return_mode: str = "chunks"


class RAGSearchResponse(BaseModel):
    """Response model for RAG search."""
    success: bool
    results: List[Dict[str, Any]]
    return_mode: str
    reranked: bool
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str


# Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        message="Archon MCP Bridge is running"
    )


@app.post("/rag/search", response_model=RAGSearchResponse)
async def search_knowledge_base(request: RAGSearchRequest):
    """
    Search Archon knowledge base using RAG.

    This endpoint calls the Archon MCP tool: mcp__archon__rag_search_knowledge_base

    Args:
        request: RAG search parameters

    Returns:
        Search results from Archon knowledge base

    Note:
        This is a placeholder implementation. In production, this would
        call the actual Archon MCP tools. Since MCP tools are only available
        within Claude Code session, you have two options:

        Option 1 (Development):
        - Use this bridge during development
        - Returns mock data structure for testing

        Option 2 (Production):
        - Deploy Archon MCP as standalone server
        - Connect to it using MCP Python SDK
        - Replace this implementation with actual MCP calls
    """
    logger.info(f"RAG search request: query='{request.query}', source_id={request.source_id}")

    # TODO: Replace with actual MCP client connection
    # For now, return error indicating MCP tools not available
    raise HTTPException(
        status_code=503,
        detail=(
            "MCP Bridge not fully implemented. "
            "This requires Archon MCP server to be running as standalone service. "
            "For development, use local FAISS stores instead."
        )
    )


@app.get("/sources")
async def get_available_sources():
    """
    Get available knowledge sources from Archon.

    This endpoint calls: mcp__archon__rag_get_available_sources

    Returns:
        List of available knowledge sources
    """
    logger.info("Getting available sources")

    # TODO: Replace with actual MCP client connection
    raise HTTPException(
        status_code=503,
        detail=(
            "MCP Bridge not fully implemented. "
            "This requires Archon MCP server to be running as standalone service."
        )
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Archon MCP Bridge Server...")
    logger.warning(
        "Note: This bridge server requires Archon MCP to be running as a standalone service. "
        "For development, consider using local FAISS stores instead."
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port from main FastAPI app
        log_level="info"
    )
