"""
Pydantic AI Agent for Sales Bike - Refactored version.

This module implements the Sales Bike Agent using Pydantic AI framework
with proper dependency injection and tool management.

Based on research from Pydantic AI docs in Archon knowledge base:
- Agent structure with deps_type parameter
- Tools with @agent.tool decorator
- System prompts with @agent.system_prompt
- Dependencies via RunContext[Deps]

References:
- Pydantic AI Dependencies (page_id: aeb96ee5-a21e-4353-a7b6-1ddd5fe4bc40)
- Pydantic AI Weather Agent (page_id: 641e75b1-6e6c-4ed1-a5d8-065e7d4d7cc0)
"""

import logging
import re
from typing import Any, Dict, List, Optional

from pydantic_ai import Agent, RunContext

from src.agent.dependencies import SalesBikeAgentDeps

logger = logging.getLogger(__name__)

# Initialize Pydantic AI agent with dependencies type
# Pattern from Pydantic AI docs: Agent(model, deps_type=YourDeps)
# Load config to ensure environment variables are loaded
import os
from src.config import settings

# Ensure OpenAI API key is in environment for Pydantic AI
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

sales_agent = Agent(
    'openai:gpt-4o',
    deps_type=SalesBikeAgentDeps,
    retries=2
)


@sales_agent.tool
async def search_products(
    ctx: RunContext[SalesBikeAgentDeps],
    query: str,
    max_price: Optional[float] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for bike products using Archon RAG.

    This tool searches the product catalog in Archon knowledge base
    and returns relevant bike recommendations.

    Based on Pydantic AI tool pattern from Weather Agent example.
    Access dependencies via ctx.deps (Pydantic AI pattern).

    Args:
        ctx: Run context with dependencies
        query: Search query (e.g., "mountain bike for trails")
        max_price: Optional maximum price filter in EUR
        top_k: Number of results to return

    Returns:
        List of product dictionaries with bike details
    """
    logger.info(f"Searching products: query='{query}', max_price={max_price}, top_k={top_k}")

    try:
        # Use local FAISS product store 
        if ctx.deps.product_store:
            logger.info("Using local FAISS product store with real data from Archon")
            # Search using local vector store
            results = ctx.deps.product_store.search(query, top_k=top_k * 2)

            # Convert results to product dictionaries
            products = []
            for product_data, score in results:
                # Filter by price if specified
                if max_price and product_data.get('price_eur', 0) > max_price:
                    continue
                products.append(product_data)

            return products[:top_k]

        # Fallback: try MCP if available
        elif ctx.deps.mcp_client:
            logger.info("Using Archon MCP for product search")
            search_query = _extract_keywords(query)
            PRODUCT_SOURCE_ID = "file_product_catalog_txt_0b304df3"

            result = await ctx.deps.mcp_client.call_tool(
                "mcp__archon__rag_search_knowledge_base",
                arguments={
                    "query": search_query,
                    "source_id": PRODUCT_SOURCE_ID,
                    "match_count": top_k * 2,
                    "return_mode": "pages"
                }
            )

            products = _parse_archon_products(result)
            if max_price:
                products = [p for p in products if p.get('price_eur', 0) <= max_price]

            return products[:top_k]

        else:
            logger.error("No product data source available (neither local store nor MCP)")
            return []

    except Exception as e:
        logger.error(f"Error searching products: {e}", exc_info=True)
        return []


@sales_agent.tool
async def search_faq(
    ctx: RunContext[SalesBikeAgentDeps],
    query: str,
    top_k: int = 2
) -> List[Dict[str, str]]:
    """
    Search FAQ knowledge base using Archon RAG.

    This tool searches the FAQ entries in Archon knowledge base
    and returns relevant Q&A pairs.

    Based on Pydantic AI tool pattern from documentation.

    Args:
        ctx: Run context with dependencies
        query: FAQ query (e.g., "delivery time", "warranty policy")
        top_k: Number of FAQ entries to return

    Returns:
        List of FAQ dictionaries with question and answer
    """
    logger.info(f"Searching FAQ: query='{query}', top_k={top_k}")

    try:
        # Use local FAISS FAQ store (already loaded with your real data!)
        if ctx.deps.faq_store:
            logger.info("Using local FAISS FAQ store with real data from Archon")
            # Search using local vector store
            results = ctx.deps.faq_store.search(query, top_k=top_k)

            # Convert results to FAQ dictionaries
            faqs = []
            for faq_data, score in results:
                faqs.append(faq_data)

            return faqs

        # Fallback: try MCP if available
        elif ctx.deps.mcp_client:
            logger.info("Using Archon MCP for FAQ search")
            search_query = _extract_faq_keywords(query)
            FAQ_SOURCE_ID = "file_faq_txt_09c5606e"

            result = await ctx.deps.mcp_client.call_tool(
                "mcp__archon__rag_search_knowledge_base",
                arguments={
                    "query": search_query,
                    "source_id": FAQ_SOURCE_ID,
                    "match_count": top_k
                }
            )

            # Parse FAQ results
            faqs = _parse_archon_faqs(result)
            return faqs

        else:
            logger.error("No FAQ data source available (neither local store nor MCP)")
            return []

    except Exception as e:
        logger.error(f"Error searching FAQ: {e}", exc_info=True)
        return []


@sales_agent.tool
async def recall_customer_preferences(
    ctx: RunContext[SalesBikeAgentDeps],
    user_id: str
) -> Dict[str, Any]:
    """
    Recall customer preferences and conversation history from Mem0.

    This tool searches Mem0 for past interactions with the customer
    to provide personalized recommendations and context.

    Based on Mem0 search() pattern from documentation.
    Reference: Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)

    Args:
        ctx: Run context with dependencies
        user_id: Customer user ID

    Returns:
        Dictionary with customer history and preferences:
        {
            "has_history": bool,
            "preferences": list of memory items,
            "summary": string summary of preferences
        }
    """
    logger.info(f"Recalling customer preferences for user_id: {user_id}")

    # Check if Mem0 client is available
    if not ctx.deps.memory_client:
        logger.warning("Mem0 client not available, returning empty history")
        return {
            "has_history": False,
            "preferences": [],
            "summary": "Memory features not enabled. No previous history available."
        }

    try:
        # Search memories using Mem0 API (from docs)
        memories = ctx.deps.memory_client.search(
            "What are this customer's bike preferences, budget, and past interactions?",
            user_id=user_id
        )

        if not memories or len(memories) == 0:
            return {
                "has_history": False,
                "preferences": [],
                "summary": "New customer, no previous history"
            }

        # Summarize memories for prompt context
        summary_parts = []
        for memory in memories[:5]:  # Top 5 most relevant
            if isinstance(memory, dict):
                text = memory.get('text', '') or memory.get('memory', '')
                if text:
                    summary_parts.append(f"- {text}")

        summary = "\n".join(summary_parts) if summary_parts else "Customer has previous interactions"

        return {
            "has_history": True,
            "preferences": memories[:5],
            "summary": summary
        }

    except Exception as e:
        logger.error(f"Error recalling customer preferences: {e}", exc_info=True)
        # Graceful fallback for new customers or API errors
        return {
            "has_history": False,
            "preferences": [],
            "summary": f"Unable to retrieve customer history: {str(e)}"
        }


@sales_agent.tool
async def save_conversation_memory(
    ctx: RunContext[SalesBikeAgentDeps],
    user_id: str,
    conversation_messages: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Save conversation to Mem0 for future recall.

    This tool stores the conversation history in Mem0 so the agent
    can recall customer preferences in future sessions.

    Based on Mem0 add() pattern from documentation.
    Reference: Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)

    Args:
        ctx: Run context with dependencies
        user_id: Customer user ID
        conversation_messages: List of message dicts with role and content
            Example: [
                {"role": "user", "content": "I need a mountain bike"},
                {"role": "assistant", "content": "I recommend..."}
            ]

    Returns:
        Dictionary with success status:
        {
            "success": bool,
            "memories_stored": int
        }
    """
    logger.info(f"Saving conversation memory for user_id: {user_id}, messages: {len(conversation_messages)}")

    # Check if Mem0 client is available
    if not ctx.deps.memory_client:
        logger.warning("Mem0 client not available, cannot save memory")
        return {
            "success": False,
            "memories_stored": 0,
            "error": "Memory features not enabled"
        }

    try:
        # Add conversation history using Mem0 API (from docs)
        result = ctx.deps.memory_client.add(
            conversation_messages,
            user_id=user_id,
            output_format="v1.0"
        )

        # Count stored memories
        memories_count = len(result) if isinstance(result, list) else (1 if result else 0)

        logger.info(f"Successfully stored {memories_count} memories for user {user_id}")

        return {
            "success": True,
            "memories_stored": memories_count
        }

    except Exception as e:
        logger.error(f"Error saving conversation memory: {e}", exc_info=True)
        return {
            "success": False,
            "memories_stored": 0,
            "error": str(e)
        }


@sales_agent.tool
async def capture_lead(
    ctx: RunContext[SalesBikeAgentDeps],
    name: str,
    email: str,
    phone: Optional[str] = None,
    interested_products: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Capture customer lead information and create in CRM.

    Use this tool when a customer shows interest in purchasing and provides
    their contact information. This will create a lead in the CRM system.

    Args:
        ctx: Run context with dependencies
        name: Customer's name
        email: Customer's email address
        phone: Optional phone number
        interested_products: Optional list of product names they're interested in

    Returns:
        Dictionary with lead creation status:
        {
            "success": bool,
            "lead_id": str (if successful),
            "message": str
        }
    """
    logger.info(f"Capturing lead: name={name}, email={email}, phone={phone}")

    try:
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return {
                "success": False,
                "message": "Invalid email format. Please provide a valid email address."
            }

        # Create lead in CRM via dependencies
        lead_result = await ctx.deps.crm_client.create_lead(
            name=name,
            email=email,
            phone=phone or "",
            notes=f"Interested in: {', '.join(interested_products)}" if interested_products else ""
        )

        if lead_result.success:
            logger.info(f"Lead created successfully: {lead_result.lead_id}")
            return {
                "success": True,
                "lead_id": lead_result.lead_id,
                "message": f"Thank you {name}! I've recorded your information. Our sales team will contact you soon at {email}."
            }
        else:
            logger.warning(f"Failed to create lead in CRM: {lead_result.error}")
            return {
                "success": False,
                "message": f"I've noted your information, but there was an issue with our system. We'll reach out to you at {email} shortly."
            }

    except Exception as e:
        logger.error(f"Error capturing lead: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"I apologize, there was an error saving your information. Please try again or contact us directly."
        }


@sales_agent.system_prompt
async def get_system_prompt(ctx: RunContext[SalesBikeAgentDeps]) -> str:
    """
    Generate system prompt with optional memory context.

    This follows the Pydantic AI system_prompt pattern where you can
    access dependencies via ctx.deps to enrich the prompt.

    Based on Pydantic AI system_prompt decorator pattern.
    Memory integration based on Mem0 documentation.

    Args:
        ctx: Run context with dependencies

    Returns:
        System prompt string with memory context if available
    """
    base_prompt = """You are a friendly and knowledgeable bike shop sales assistant.

Your goal is to help customers find the perfect bike by:
1. IMMEDIATELY search for products when customers mention bike needs or types
2. Show specific bike recommendations from our catalog
3. Answer questions about bikes, policies, and services
4. Guide interested customers through the purchase process

Guidelines:
- ALWAYS use the search_products tool when a customer mentions any bike type, need, or budget
- Show products FIRST, then ask follow-up questions if needed
- Be conversational but action-oriented
- Provide specific product recommendations with details
- Explain technical features in simple terms
- Focus on matching bikes to customer's use case and budget

IMPORTANT: Don't ask clarifying questions before searching - search first based on what they say, then refine!

PURCHASE INTENT DETECTION & LEAD CAPTURE:
When customers show purchase intent, use the capture_lead tool to collect their information:

Purchase Intent Signals:
- "I want to buy this bike"
- "I'm interested in purchasing"
- "How do I order?"
- "Can I get this bike?"
- "I'd like to proceed with this one"
- "This looks perfect, what's next?"

Lead Capture Flow:
1. When you detect purchase intent, express enthusiasm and confirm their choice
2. Ask for their name: "Great choice! May I have your name?"
3. Ask for their email: "And what's the best email to reach you at?"
4. Optionally ask for phone: "Would you also like to provide a phone number?"
5. Use the capture_lead tool with collected information
6. Confirm successful lead capture: "Thank you [Name]! I've recorded your information. Our sales team will contact you soon at [email] to finalize your purchase."

Important:
- Always get explicit consent before using the capture_lead tool
- Be natural - don't rush the customer
- If they're not ready to provide info, that's okay - continue helping them
- Store their interested product names in the interested_products parameter"""

    # Try to get user_id from context/session to recall memories
    # In a real implementation, this would come from the session
    # For now, we check if memory client is available
    if ctx.deps.memory_client:
        # Add note about memory capability
        memory_note = """\n\nIMPORTANT: You have access to customer memory via the recall_customer_preferences tool.
- For returning customers, use this tool to recall their previous preferences and conversations
- Personalize recommendations based on their history
- Reference past interactions naturally (e.g., "I remember you were interested in...")
- Use the save_conversation_memory tool to store important preferences for future visits"""

        return base_prompt + memory_note

    return base_prompt


# Helper functions for keyword extraction and parsing

def _extract_keywords(query: str) -> str:
    """
    Extract 2-5 keywords from query for better Archon RAG search.

    Following Archon best practice: keep queries SHORT and FOCUSED.

    Args:
        query: Full user query

    Returns:
        Extracted keywords (2-5 words)
    """
    # Key bike-related terms to prioritize
    bike_types = ["mountain", "road", "city", "hybrid", "electric", "gravel", "touring"]
    features = ["lightweight", "carbon", "aluminum", "disc", "trail", "commute"]

    query_lower = query.lower()
    keywords = []

    # Extract bike types
    for btype in bike_types:
        if btype in query_lower:
            keywords.append(btype)

    # Extract features
    for feature in features:
        if feature in query_lower:
            keywords.append(feature)

    # If no keywords found, use first few meaningful words
    if not keywords:
        words = re.findall(r'\b[a-z]{3,}\b', query_lower)
        keywords = words[:3]

    # Return 2-5 keywords
    return " ".join(keywords[:5]) if keywords else query[:50]


def _extract_faq_keywords(query: str) -> str:
    """
    Extract FAQ-specific keywords.

    Args:
        query: FAQ query

    Returns:
        Extracted keywords
    """
    faq_terms = ["warranty", "delivery", "return", "shipping", "payment", "assembly", "maintenance"]

    query_lower = query.lower()
    keywords = []

    for term in faq_terms:
        if term in query_lower:
            keywords.append(term)

    if not keywords:
        words = re.findall(r'\b[a-z]{3,}\b', query_lower)
        keywords = words[:3]

    return " ".join(keywords) if keywords else query[:50]


def _parse_archon_products(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Archon RAG results into product dictionaries.

    Args:
        result: Archon RAG search result

    Returns:
        List of product dictionaries
    """
    products = []

    try:
        if not result.get("success"):
            logger.warning("Archon product search returned success=False")
            return products

        results = result.get("results", [])

        for item in results:
            # Parse product from page content
            content = item.get("content", "")
            if not content:
                continue

            # Extract product fields (simplified parsing)
            # In real implementation, would parse structured JSON from content
            product = {
                "id": item.get("page_id", "")[:8],
                "name": _extract_field(content, "Name:"),
                "type": _extract_field(content, "Type:"),
                "brand": _extract_field(content, "Brand:"),
                "price_eur": _extract_price(content),
                "frame_material": _extract_field(content, "Frame:"),
                "gears": _extract_field(content, "Gears:"),
                "brakes": _extract_field(content, "Brakes:"),
                "intended_use": _extract_list(content, "Use:"),
            }

            products.append(product)

    except Exception as e:
        logger.error(f"Error parsing Archon products: {e}", exc_info=True)

    return products


def _parse_archon_faqs(result: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Parse Archon RAG results into FAQ dictionaries.

    Args:
        result: Archon RAG search result

    Returns:
        List of FAQ dictionaries with question and answer
    """
    faqs = []

    try:
        if not result.get("success"):
            logger.warning("Archon FAQ search returned success=False")
            return faqs

        results = result.get("results", [])

        for item in results:
            content = item.get("content", "")
            if not content:
                continue

            # Parse Q&A format
            lines = content.split('\n')
            question = ""
            answer = ""

            for line in lines:
                if line.startswith("Q:") or line.startswith("Question:"):
                    question = line.split(":", 1)[1].strip()
                elif line.startswith("A:") or line.startswith("Answer:"):
                    answer = line.split(":", 1)[1].strip()

            if question and answer:
                faqs.append({
                    "question": question,
                    "answer": answer
                })

    except Exception as e:
        logger.error(f"Error parsing Archon FAQs: {e}", exc_info=True)

    return faqs


def _extract_field(content: str, field_name: str) -> str:
    """Extract a field value from content."""
    pattern = f"{field_name}\\s*([^\\n]+)"
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"


def _extract_price(content: str) -> float:
    """Extract price from content."""
    pattern = r"Price:?\s*€?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        price_str = match.group(1).replace(',', '')
        try:
            return float(price_str)
        except ValueError:
            return 0.0
    return 0.0


def _extract_list(content: str, field_name: str) -> List[str]:
    """Extract list field from content."""
    pattern = f"{field_name}\\s*([^\\n]+)"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        return [item.strip() for item in value.split(',')]
    return []
