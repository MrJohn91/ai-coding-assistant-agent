"""Interest signal detection."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def detect_interest(message: str, context: dict) -> bool:
    """Detect if user shows buying interest.

    Args:
        message: User message
        context: Conversation context

    Returns:
        True if interest detected, False otherwise
    """
    message_lower = message.lower()

    # Strong interest keywords
    strong_keywords = [
        "interested",
        "i want",
        "i'd like",
        "i'll take",
        "buy",
        "purchase",
        "order",
        "how can i buy",
        "how do i order",
        "looks perfect",
        "sounds great",
        "that's the one",
        "i like this",
        "i love",
    ]

    # Check for strong signals
    for keyword in strong_keywords:
        if keyword in message_lower:
            logger.info(f"Strong interest detected: '{keyword}' in message")
            return True

    # Contextual signals (after product recommendation)
    if context.get("recommended_products"):
        contextual_keywords = [
            "yes",
            "perfect",
            "great",
            "good",
            "that works",
            "sounds good",
            "definitely",
        ]

        for keyword in contextual_keywords:
            if keyword in message_lower and len(message_lower.split()) <= 3:
                logger.info(f"Contextual interest detected: '{keyword}'")
                return True

    return False
