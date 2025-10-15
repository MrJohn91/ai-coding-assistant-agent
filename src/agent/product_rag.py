"""Product recommendation using RAG - Archon MCP version."""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from src.agent.prompts import PRODUCT_RECOMMENDATION_PROMPT
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class ProductRAG:
    """Product recommendation using Archon RAG."""

    # Archon source ID for product catalog
    PRODUCT_SOURCE_ID = "file_product_catalog_txt_0b304df3"

    def __init__(self, mcp_client: Any, llm: LLMProvider):
        """Initialize product RAG with Archon MCP.

        Args:
            mcp_client: Archon MCP client for RAG search
            llm: LLM provider
        """
        self.mcp_client = mcp_client
        self.llm = llm

    async def search_products(
        self, query: str, top_k: int = 5, max_price: Optional[int] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Search for products matching query using Archon RAG.

        Args:
            query: Search query
            top_k: Number of results
            max_price: Optional maximum price filter

        Returns:
            List of (product_dict, score) tuples
        """
        logger.info(f"Searching products via Archon: query='{query}', top_k={top_k}, max_price={max_price}")

        # Extract budget from query if present
        if max_price is None:
            max_price = self._extract_budget(query)

        # Build search query for bike characteristics
        search_query = self._build_search_query(query)

        # Search Archon RAG knowledge base
        try:
            result = await self.mcp_client.call_tool(
                "mcp__archon__rag_search_knowledge_base",
                arguments={
                    "query": search_query,
                    "source_id": self.PRODUCT_SOURCE_ID,
                    "match_count": top_k * 2,  # Get more to filter by price
                    "return_mode": "pages"
                }
            )

            products = self._parse_archon_results(result, max_price, top_k)
            logger.info(f"Found {len(products)} products from Archon")
            return products

        except Exception as e:
            logger.error(f"Failed to search Archon RAG: {e}")
            return []

    async def generate_recommendation(
        self,
        query: str,
        products: List[Tuple[Dict[str, Any], float]],
        bike_type: Optional[str] = None,
        budget: Optional[int] = None,
        intended_use: List[str] = None,
    ) -> str:
        """Generate natural language product recommendation.

        Args:
            query: Customer query
            products: Retrieved products with scores
            bike_type: Customer's bike type preference
            budget: Customer's budget
            intended_use: Intended use cases

        Returns:
            Natural language recommendation
        """
        if not products:
            return "I'm sorry, I couldn't find any bikes matching your criteria. Could you tell me more about what you're looking for?"

        # Format products for prompt
        products_text = self._format_products(products)

        # Build prompt
        prompt = PRODUCT_RECOMMENDATION_PROMPT.format(
            query=query,
            bike_type=bike_type or "Not specified",
            budget=f"€{budget}" if budget else "Not specified",
            intended_use=", ".join(intended_use) if intended_use else "Not specified",
            products=products_text,
        )

        # Generate response
        messages = [
            {"role": "system", "content": "You are a helpful bike shop sales assistant."},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm.generate(messages, temperature=0.7, max_tokens=300)
            return response

        except Exception as e:
            logger.error(f"Failed to generate recommendation: {e}")
            # Fallback to simple template
            return self._fallback_recommendation(products)

    def _extract_budget(self, query: str) -> Optional[int]:
        """Extract budget from query text.

        Args:
            query: Query text

        Returns:
            Budget amount or None
        """
        # Look for patterns like "under 1000", "below €1500", "max 2000"
        patterns = [
            r"under (?:€)?(\d+)",
            r"below (?:€)?(\d+)",
            r"max (?:€)?(\d+)",
            r"budget (?:of )?(?:€)?(\d+)",
            r"(?:€)?(\d+) (?:euro|EUR|eur)",
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                budget = int(match.group(1))
                logger.info(f"Extracted budget: €{budget}")
                return budget

        return None

    def _build_search_query(self, query: str) -> str:
        """Build optimized search query for Archon (2-5 keywords).

        Args:
            query: Customer query

        Returns:
            Optimized search query
        """
        # Extract key bike-related terms
        keywords = []

        # Bike types
        bike_types = ["mountain", "city", "road", "electric", "hybrid", "gravel", "bmx"]
        for bike_type in bike_types:
            if bike_type in query.lower():
                keywords.append(bike_type)

        # Features
        features = ["aluminum", "carbon", "steel", "hydraulic", "disc", "suspension"]
        for feature in features:
            if feature in query.lower():
                keywords.append(feature)

        # Use cases
        uses = ["trail", "commuting", "racing", "touring", "off-road"]
        for use in uses:
            if use in query.lower():
                keywords.append(use)

        # If no keywords found, use first few meaningful words
        if not keywords:
            words = [w for w in query.lower().split() if len(w) > 3][:3]
            keywords = words if words else ["bike"]

        # Limit to 5 keywords max
        return " ".join(keywords[:5])

    def _parse_archon_results(
        self,
        result: Dict[str, Any],
        max_price: Optional[int],
        top_k: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Parse Archon RAG results into product list.

        Args:
            result: Archon RAG result
            max_price: Maximum price filter
            top_k: Number of results to return

        Returns:
            List of (product_dict, score) tuples
        """
        try:
            # Parse JSON result
            if isinstance(result, str):
                data = json.loads(result)
            else:
                data = result

            if not data.get("success"):
                logger.error(f"Archon RAG error: {data.get('error')}")
                return []

            products = []
            for page in data.get("results", []):
                # Extract product data from content
                content = page.get("content", "")
                product = self._parse_product_from_content(content)

                if product:
                    # Apply price filter
                    if max_price and product.get("price_eur", 0) > max_price:
                        continue

                    # Use relevance score (similarity from vector search)
                    score = page.get("similarity", 0.0)
                    products.append((product, score))

            # Sort by score and return top_k
            products.sort(key=lambda x: x[1], reverse=True)
            return products[:top_k]

        except Exception as e:
            logger.error(f"Failed to parse Archon results: {e}")
            return []

    def _parse_product_from_content(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse product JSON from content string.

        Args:
            content: Raw content from Archon

        Returns:
            Product dictionary or None
        """
        try:
            # Content should be JSON product data
            product = json.loads(content)
            return product
        except Exception:
            # Try to extract JSON from text
            try:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start >= 0 and end > start:
                    product = json.loads(content[start:end])
                    return product
            except Exception as e:
                logger.error(f"Failed to parse product content: {e}")
        return None

    def _format_products(self, products: List[Tuple[Dict[str, Any], float]]) -> str:
        """Format products for LLM prompt.

        Args:
            products: List of (product_dict, score) tuples

        Returns:
            Formatted product text
        """
        lines = []
        for idx, (product, score) in enumerate(products, 1):
            lines.append(f"{idx}. {product.get('name', 'Unknown')}")
            lines.append(f"   Brand: {product.get('brand', 'N/A')}")
            lines.append(f"   Type: {product.get('type', 'N/A')}")
            lines.append(f"   Price: €{product.get('price_eur', 0)}")
            lines.append(f"   Features: {product.get('frame_material', 'N/A')} frame, {product.get('suspension', 'N/A')}, {product.get('brakes', 'N/A')}")
            lines.append(f"   Gears: {product.get('gears', 'N/A')}, Wheel size: {product.get('wheel_size', 'N/A')}\", Weight: {product.get('weight_kg', 'N/A')}kg")

            intended_use = product.get('intended_use', [])
            if isinstance(intended_use, list):
                lines.append(f"   Intended use: {', '.join(intended_use)}")

            lines.append(f"   Color: {product.get('color', 'N/A')}")

            # Add electric bike details if present
            if product.get('motor_power_w'):
                lines.append(f"   Motor: {product.get('motor_power_w')}W, Battery: {product.get('battery_capacity_wh')}Wh, Range: {product.get('range_km')}km")

            lines.append("")

        return "\n".join(lines)

    def _fallback_recommendation(self, products: List[Tuple[Dict[str, Any], float]]) -> str:
        """Generate simple fallback recommendation.

        Args:
            products: List of (product_dict, score) tuples

        Returns:
            Simple recommendation text
        """
        if not products:
            return "I couldn't find any suitable bikes. Could you provide more details?"

        # Recommend top 2 products
        top_products = products[:2]

        lines = ["Based on your needs, I recommend:"]

        for product, _ in top_products:
            intended_use = product.get('intended_use', [])
            use_str = ', '.join(intended_use[:2]) if isinstance(intended_use, list) else "various activities"

            lines.append(
                f"\n- {product.get('name', 'Unknown')} by {product.get('brand', 'N/A')} (€{product.get('price_eur', 0)}): "
                f"{product.get('frame_material', 'N/A')} frame, {product.get('gears', 'N/A')} gears, perfect for {use_str}."
            )

        lines.append("\n\nWould you like more details about any of these bikes?")

        return "".join(lines)
