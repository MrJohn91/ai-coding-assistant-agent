"""Intent detection for conversation routing."""

import json
import logging
from enum import Enum
from typing import Dict, List

from src.agent.prompts import INTENT_EXAMPLES, build_intent_prompt
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class Intent(str, Enum):
    """Intent types for user messages."""

    PRODUCT_INQUIRY = "PRODUCT_INQUIRY"
    FAQ_QUESTION = "FAQ_QUESTION"
    LEAD_INFO = "LEAD_INFO"
    INTEREST_SIGNAL = "INTEREST_SIGNAL"
    CHITCHAT = "CHITCHAT"


async def detect_intent(
    message: str, history: List[Dict[str, str]], llm: LLMProvider
) -> Dict[str, any]:
    """Detect user intent using LLM.

    Args:
        message: User message
        history: Conversation history
        llm: LLM provider

    Returns:
        Dict with intent and confidence score
    """
    # Build prompt
    intent_prompt = build_intent_prompt(message, history)

    # Create messages for LLM
    messages = [
        {"role": "system", "content": INTENT_EXAMPLES},
        {"role": "user", "content": intent_prompt},
    ]

    try:
        # Get intent from LLM
        response = await llm.generate_json(messages, temperature=0.3)

        intent_str = response.get("intent", "CHITCHAT")
        confidence = response.get("confidence", 0.5)

        # Validate intent
        try:
            intent = Intent(intent_str)
        except ValueError:
            logger.warning(f"Invalid intent from LLM: {intent_str}, defaulting to CHITCHAT")
            intent = Intent.CHITCHAT
            confidence = 0.5

        logger.info(f"Detected intent: {intent.value} (confidence: {confidence})")

        return {"intent": intent, "confidence": confidence}

    except Exception as e:
        logger.error(f"Intent detection failed: {e}")
        # Fallback to keyword matching
        return _fallback_intent_detection(message)


def _fallback_intent_detection(message: str) -> Dict[str, any]:
    """Fallback intent detection using keyword matching.

    Args:
        message: User message

    Returns:
        Dict with intent and confidence
    """
    message_lower = message.lower()

    # Product inquiry keywords
    product_keywords = [
        "bike", "bicycle", "mountain", "road", "city", "electric", "ebike",
        "recommend", "looking for", "need", "want", "price", "cost"
    ]
    if any(kw in message_lower for kw in product_keywords):
        return {"intent": Intent.PRODUCT_INQUIRY, "confidence": 0.7}

    # FAQ keywords
    faq_keywords = [
        "warranty", "delivery", "ship", "return", "payment", "financing",
        "repair", "maintenance", "test", "insurance", "spare parts"
    ]
    if any(kw in message_lower for kw in faq_keywords):
        return {"intent": Intent.FAQ_QUESTION, "confidence": 0.7}

    # Interest signal keywords
    interest_keywords = [
        "interested", "buy", "purchase", "order", "like this", "want this",
        "perfect", "great", "sounds good"
    ]
    if any(kw in message_lower for kw in interest_keywords):
        return {"intent": Intent.INTEREST_SIGNAL, "confidence": 0.8}

    # Lead info (email, phone patterns)
    if "@" in message or "+" in message or message.replace("-", "").replace(" ", "").isdigit():
        return {"intent": Intent.LEAD_INFO, "confidence": 0.9}

    # Default to chitchat
    return {"intent": Intent.CHITCHAT, "confidence": 0.6}
