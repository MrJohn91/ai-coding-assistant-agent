"""Pytest configuration and shared fixtures."""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce noise in tests
    os.environ["CRM_API_URL"] = "https://test-crm.example.com"
