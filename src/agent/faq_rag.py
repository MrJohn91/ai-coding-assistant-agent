"""FAQ answering using RAG - Archon MCP version."""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from src.agent.prompts import FAQ_ANSWER_PROMPT
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class FAQRAG:
    """FAQ answering using Archon RAG."""

    # Archon source ID for FAQ
    FAQ_SOURCE_ID = "file_faq_txt_09c5606e"

    def __init__(self, mcp_client: Any, llm: LLMProvider):
        """Initialize FAQ RAG with Archon MCP.

        Args:
            mcp_client: Archon MCP client for RAG search
            llm: LLM provider
        """
        self.mcp_client = mcp_client
        self.llm = llm

    async def search_faq(self, query: str, top_k: int = 2) -> List[Tuple[Dict[str, str], float]]:
        """Search for relevant FAQ entries using Archon RAG.

        Args:
            query: Search query
            top_k: Number of results

        Returns:
            List of (faq_dict, score) tuples
        """
        logger.info(f"Searching FAQ via Archon: query='{query}', top_k={top_k}")

        # Build search query (extract key question words)
        search_query = self._build_search_query(query)

        try:
            result = await self.mcp_client.call_tool(
                "mcp__archon__rag_search_knowledge_base",
                arguments={
                    "query": search_query,
                    "source_id": self.FAQ_SOURCE_ID,
                    "match_count": top_k,
                    "return_mode": "pages"
                }
            )

            faqs = self._parse_archon_results(result)
            logger.info(f"Found {len(faqs)} FAQ entries from Archon")
            return faqs

        except Exception as e:
            logger.error(f"Failed to search Archon FAQ: {e}")
            return []

    async def generate_answer(
        self, query: str, faq_entries: List[Tuple[Dict[str, str], float]]
    ) -> str:
        """Generate natural language answer from FAQ entries.

        Args:
            query: Customer question
            faq_entries: Retrieved FAQ entries with scores

        Returns:
            Natural language answer
        """
        if not faq_entries:
            return "I'm not sure about that. Could you rephrase your question or contact our customer service?"

        # Format FAQ entries for prompt
        faq_text = self._format_faq_entries(faq_entries)

        # Build prompt
        prompt = FAQ_ANSWER_PROMPT.format(
            query=query,
            faq_entries=faq_text,
        )

        # Generate response
        messages = [
            {"role": "system", "content": "You are a helpful customer service assistant."},
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.llm.generate(messages, temperature=0.5, max_tokens=200)
            return response

        except Exception as e:
            logger.error(f"Failed to generate FAQ answer: {e}")
            # Fallback to direct FAQ answer
            return self._fallback_answer(faq_entries)

    def _build_search_query(self, query: str) -> str:
        """Build optimized search query for Archon (2-5 keywords).

        Args:
            query: Customer question

        Returns:
            Optimized search query
        """
        # Extract key FAQ-related terms
        keywords = []

        # Common FAQ topics
        topics = ["warranty", "delivery", "return", "payment", "shipping", "size", "maintenance"]
        for topic in topics:
            if topic in query.lower():
                keywords.append(topic)

        # Question words
        question_words = ["what", "how", "when", "where", "why", "can", "do"]
        words = query.lower().split()
        for word in words:
            if word not in question_words and len(word) > 3 and word not in keywords:
                keywords.append(word)
                if len(keywords) >= 5:
                    break

        # If no keywords, use first few words
        if not keywords:
            keywords = [w for w in words if len(w) > 3][:3]

        return " ".join(keywords[:5])

    def _parse_archon_results(self, result: Dict[str, Any]) -> List[Tuple[Dict[str, str], float]]:
        """Parse Archon RAG results into FAQ list.

        Args:
            result: Archon RAG result

        Returns:
            List of (faq_dict, score) tuples
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

            faqs = []
            for page in data.get("results", []):
                content = page.get("content", "")
                faq = self._parse_faq_from_content(content)

                if faq:
                    score = page.get("similarity", 0.0)
                    faqs.append((faq, score))

            return faqs

        except Exception as e:
            logger.error(f"Failed to parse Archon FAQ results: {e}")
            return []

    def _parse_faq_from_content(self, content: str) -> Optional[Dict[str, str]]:
        """Parse FAQ from content string.

        Args:
            content: Raw content from Archon

        Returns:
            FAQ dictionary with question and answer
        """
        try:
            # Try to extract Q: and A: format
            lines = content.split('\n')
            question = None
            answer = None

            for i, line in enumerate(lines):
                line = line.strip()
                if line.startswith("Q:") or line.startswith("Question:"):
                    question = line.split(":", 1)[1].strip()
                elif line.startswith("A:") or line.startswith("Answer:"):
                    answer = line.split(":", 1)[1].strip()
                    # Collect multi-line answers
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].strip().startswith("Q:"):
                            answer += " " + lines[j].strip()
                        else:
                            break

            if question and answer:
                return {"question": question, "answer": answer}

            # Fallback: treat entire content as answer
            return {"question": "General information", "answer": content.strip()}

        except Exception as e:
            logger.error(f"Failed to parse FAQ content: {e}")
            return None

    def _format_faq_entries(self, entries: List[Tuple[Dict[str, str], float]]) -> str:
        """Format FAQ entries for LLM prompt.

        Args:
            entries: List of (faq_dict, score) tuples

        Returns:
            Formatted FAQ text
        """
        lines = []
        for idx, (entry, score) in enumerate(entries, 1):
            lines.append(f"FAQ {idx}:")
            lines.append(f"Q: {entry.get('question', 'Unknown')}")
            lines.append(f"A: {entry.get('answer', 'N/A')}")
            lines.append("")

        return "\n".join(lines)

    def _fallback_answer(self, entries: List[Tuple[Dict[str, str], float]]) -> str:
        """Generate simple fallback answer.

        Args:
            entries: List of (faq_dict, score) tuples

        Returns:
            Simple answer text
        """
        if not entries:
            return "I don't have information about that. Please contact our customer service."

        # Return the top FAQ answer directly
        top_entry, _ = entries[0]
        return top_entry.get('answer', "I don't have specific information about that.")
