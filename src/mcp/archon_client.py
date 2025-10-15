"""Archon MCP client wrapper for RAG operations."""

import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class ArchonMCPClient:
    """
    Client for Archon MCP server via HTTP bridge.

    This client connects to the MCP bridge server which exposes
    Archon MCP tools via HTTP endpoints.

    Architecture:
    - FastAPI app -> ArchonMCPClient (HTTP) -> MCP Bridge -> Archon MCP Server

    Usage:
        client = ArchonMCPClient(bridge_url="http://localhost:8001")
        result = await client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            {"query": "mountain bike", "source_id": "...", "match_count": 5}
        )
    """

    def __init__(self, bridge_url: str = "http://localhost:8001"):
        """Initialize Archon MCP client.

        Args:
            bridge_url: URL of the MCP bridge server
        """
        self.bridge_url = bridge_url.rstrip("/")
        self.client: Optional[httpx.AsyncClient] = None
        logger.info(f"Initialized ArchonMCPClient with bridge URL: {self.bridge_url}")

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call an Archon MCP tool via the bridge server.

        Args:
            tool_name: Name of the MCP tool (e.g., "mcp__archon__rag_search_knowledge_base")
            arguments: Tool arguments

        Returns:
            Tool result as returned by Archon MCP

        Raises:
            httpx.HTTPError: If bridge server is unreachable
            ValueError: If tool name is not supported
        """
        await self._ensure_client()

        logger.info(f"Calling MCP tool via bridge: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            # Map MCP tool names to bridge endpoints
            if tool_name == "mcp__archon__rag_search_knowledge_base":
                response = await self.client.post(
                    f"{self.bridge_url}/rag/search",
                    json={
                        "query": arguments.get("query"),
                        "source_id": arguments.get("source_id"),
                        "match_count": arguments.get("match_count", 5),
                        "return_mode": arguments.get("return_mode", "chunks")
                    }
                )
                response.raise_for_status()
                return response.json()

            elif tool_name == "mcp__archon__rag_get_available_sources":
                response = await self.client.get(f"{self.bridge_url}/sources")
                response.raise_for_status()
                return response.json()

            else:
                raise ValueError(f"Unsupported MCP tool: {tool_name}")

        except httpx.HTTPStatusError as e:
            logger.error(f"MCP bridge returned error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to MCP bridge at {self.bridge_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}", exc_info=True)
            raise

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None
            logger.info("Closed ArchonMCPClient HTTP client")
