"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestConversationAPI:
    """Test conversation API endpoints."""

    def test_create_conversation(self, client):
        """Test creating new conversation."""
        response = client.post("/api/v1/conversations")

        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert len(data["session_id"]) > 0

    def test_send_message(self, client):
        """Test sending message."""
        # Create conversation
        create_response = client.post("/api/v1/conversations")
        session_id = create_response.json()["session_id"]

        # Send message
        response = client.post(
            f"/api/v1/conversations/{session_id}/messages",
            json={"message": "Hello, I'm looking for a bike"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert data["session_id"] == session_id

    def test_get_conversation_history(self, client):
        """Test retrieving conversation history."""
        # Create conversation and send message
        create_response = client.post("/api/v1/conversations")
        session_id = create_response.json()["session_id"]

        client.post(
            f"/api/v1/conversations/{session_id}/messages",
            json={"message": "Test message"}
        )

        # Get history
        response = client.get(f"/api/v1/conversations/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert "state" in data
        assert len(data["messages"]) >= 2  # User + assistant messages

    def test_delete_conversation(self, client):
        """Test deleting conversation."""
        # Create conversation
        create_response = client.post("/api/v1/conversations")
        session_id = create_response.json()["session_id"]

        # Delete
        response = client.delete(f"/api/v1/conversations/{session_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/conversations/{session_id}")
        assert get_response.status_code == 404

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_invalid_session(self, client):
        """Test sending message to invalid session."""
        response = client.post(
            "/api/v1/conversations/invalid-session-id/messages",
            json={"message": "Hello"}
        )

        assert response.status_code == 404
