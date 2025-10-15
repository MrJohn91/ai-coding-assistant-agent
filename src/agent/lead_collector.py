"""Lead data collection with validation."""

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class LeadCollector:
    """Lead data collection and validation."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.

        Args:
            email: Email address

        Returns:
            True if valid, False otherwise
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone format.

        Args:
            phone: Phone number

        Returns:
            True if valid, False otherwise
        """
        # Remove spaces, dashes, parentheses
        cleaned = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")

        # Check for international format or local format
        pattern = r"^\+?[0-9]{7,15}$"
        return bool(re.match(pattern, cleaned))

    @staticmethod
    def extract_name(message: str) -> Optional[str]:
        """Extract name from message.

        Args:
            message: User message

        Returns:
            Extracted name or None
        """
        # Simple extraction: assume message contains name
        # Skip common phrases
        skip_phrases = ["my name is", "i'm", "i am", "it's", "this is"]

        message_lower = message.lower()
        for phrase in skip_phrases:
            if phrase in message_lower:
                # Extract text after phrase
                parts = message_lower.split(phrase)
                if len(parts) > 1:
                    name = parts[1].strip().strip(".,!?")
                    # Capitalize properly
                    return " ".join(word.capitalize() for word in name.split())

        # If no phrase found, assume entire message is name (if reasonable length)
        if 2 <= len(message.split()) <= 4 and message.replace(" ", "").isalpha():
            return " ".join(word.capitalize() for word in message.split())

        return None

    @staticmethod
    def extract_email(message: str) -> Optional[str]:
        """Extract email from message.

        Args:
            message: User message

        Returns:
            Extracted email or None
        """
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(pattern, message)

        if match:
            email = match.group(0)
            if LeadCollector.validate_email(email):
                return email.lower()

        return None

    @staticmethod
    def extract_phone(message: str) -> Optional[str]:
        """Extract phone from message.

        Args:
            message: User message

        Returns:
            Extracted phone or None
        """
        # Look for phone patterns
        patterns = [
            r"\+?\d[\d\s\-\(\)]{6,}\d",  # General phone pattern
            r"\+\d{1,3}\s?\d{7,14}",  # International format
        ]

        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                phone = match.group(0)
                if LeadCollector.validate_phone(phone):
                    # Normalize format
                    return phone.strip()

        return None

    @staticmethod
    def extract_lead_info(message: str, expected_field: str) -> Tuple[Optional[str], str]:
        """Extract lead information based on expected field.

        Args:
            message: User message
            expected_field: Field being collected (name, email, phone)

        Returns:
            Tuple of (extracted_value, error_message)
        """
        if expected_field == "name":
            name = LeadCollector.extract_name(message)
            if name:
                return name, ""
            return None, "I didn't catch your name. Could you please provide it?"

        elif expected_field == "email":
            email = LeadCollector.extract_email(message)
            if email:
                return email, ""
            return None, "That doesn't look like a valid email address. Could you try again?"

        elif expected_field == "phone":
            phone = LeadCollector.extract_phone(message)
            if phone:
                return phone, ""
            return None, "That doesn't seem to be a valid phone number. Please provide a valid number."

        return None, "Unknown field"
