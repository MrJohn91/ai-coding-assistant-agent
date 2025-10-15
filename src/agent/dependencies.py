"""
Pydantic AI Dependencies for Sales Bike Agent.

This module defines the dependencies structure following Pydantic AI's
dependency injection pattern from their documentation.

Based on research from Pydantic AI docs in Archon knowledge base:
- Dependencies defined as dataclass
- Passed to Agent via deps_type parameter
- Accessed in tools/system_prompts via RunContext[Deps]

Reference: Pydantic AI Dependencies documentation
(page_id: aeb96ee5-a21e-4353-a7b6-1ddd5fe4bc40)
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import httpx
from mem0 import MemoryClient


@dataclass
class SalesBikeAgentDeps:
    """
    Dependencies for Sales Bike Agent (Pydantic AI pattern).

    This dataclass holds all external dependencies that the agent needs:
    - Archon MCP for product/FAQ search (optional - fallback to local stores)
    - Mem0 for conversation memory
    - CRM client for lead management
    - Session store for conversation state
    - HTTP client for async requests
    - Local vector stores (FAISS) for product/FAQ search when MCP not available

    Usage:
        agent = Agent('openai:gpt-4o', deps_type=SalesBikeAgentDeps)

        @agent.tool
        async def my_tool(ctx: RunContext[SalesBikeAgentDeps]):
            # Access dependencies via ctx.deps
            result = await ctx.deps.mcp_client.call_tool(...)
    """

    # Archon MCP client for product catalog and FAQ search (optional)
    mcp_client: Optional[Any] = None

    # Mem0 client for conversation memory (customer preferences, history)
    memory_client: Optional[MemoryClient] = None

    # CRM client for lead capture and management
    crm_client: Any = None

    # Session store for managing conversation state
    session_store: Any = None

    # HTTP client for async requests (if needed by tools)
    http_client: Optional[httpx.AsyncClient] = None

    # Local FAISS vector stores (fallback when MCP not available)
    product_store: Any = None
    faq_store: Any = None
    llm: Any = None
