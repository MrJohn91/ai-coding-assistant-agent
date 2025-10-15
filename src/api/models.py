"""API request/response models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductRecommendation(BaseModel):
    """Product recommendation in API response."""

    id: int
    name: str
    type: str
    brand: str
    price_eur: int
    key_features: str
    intended_use: List[str]


class MessageRequest(BaseModel):
    """Request model for sending a message."""

    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Conversation session ID")


class MessageResponse(BaseModel):
    """Response model for agent message."""

    session_id: str
    response: str
    products: Optional[List[ProductRecommendation]] = None
    lead_created: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history."""

    session_id: str
    messages: List[dict]
    state: str
    created_at: str


class ConversationCreateResponse(BaseModel):
    """Response when creating a new conversation."""

    session_id: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str = "1.0.0"
