"""Unit tests for lead collector."""

import pytest

from src.agent.lead_collector import LeadCollector


@pytest.fixture
def collector():
    """Create lead collector instance."""
    return LeadCollector()


class TestLeadCollector:
    """Test lead data collection and validation."""

    def test_extract_name_valid(self, collector):
        """Test extracting valid names."""
        name, error = collector.extract_lead_info("John Doe", "name")
        assert name == "John Doe"
        assert error == ""

        name, error = collector.extract_lead_info("María García", "name")
        assert name == "María García"
        assert error == ""

    def test_extract_name_invalid(self, collector):
        """Test rejecting invalid names."""
        name, error = collector.extract_lead_info("", "name")
        assert name is None
        assert "name" in error.lower()

        name, error = collector.extract_lead_info("   ", "name")
        assert name is None
        assert error is not None

    def test_extract_email_valid(self, collector):
        """Test extracting valid emails."""
        email, error = collector.extract_lead_info("john@example.com", "email")
        assert email == "john@example.com"
        assert error == ""

        email, error = collector.extract_lead_info("user.name+tag@domain.co.uk", "email")
        assert email == "user.name+tag@domain.co.uk"
        assert error == ""

    def test_extract_email_invalid(self, collector):
        """Test rejecting invalid emails."""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
        ]

        for invalid_email in invalid_emails:
            email, error = collector.extract_lead_info(invalid_email, "email")
            assert email is None
            assert "email" in error.lower()

    def test_extract_phone_valid(self, collector):
        """Test extracting valid phone numbers."""
        valid_phones = [
            "+491234567890",
            "+1-555-123-4567",
            "004912345678",
            "01234567890",
        ]

        for phone in valid_phones:
            result, error = collector.extract_lead_info(phone, "phone")
            assert result is not None
            assert error == ""

    def test_extract_phone_invalid(self, collector):
        """Test rejecting invalid phone numbers."""
        invalid_phones = [
            "12345",  # Too short
            "not-a-phone",
            "abc123",
        ]

        for phone in invalid_phones:
            result, error = collector.extract_lead_info(phone, "phone")
            assert result is None
            assert "phone" in error.lower()
