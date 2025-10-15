"""Conversation session management."""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Dict, List, Optional


class ConversationState(str, Enum):
    """Conversation state machine states."""

    GREETING = "GREETING"
    DISCOVERY = "DISCOVERY"
    RECOMMENDATION = "RECOMMENDATION"
    INTEREST_CONFIRMED = "INTEREST_CONFIRMED"
    LEAD_COLLECTION = "LEAD_COLLECTION"
    NAME_COLLECTED = "NAME_COLLECTED"
    EMAIL_COLLECTED = "EMAIL_COLLECTED"
    PHONE_COLLECTED = "PHONE_COLLECTED"
    LEAD_CREATED = "LEAD_CREATED"
    FAQ_MODE = "FAQ_MODE"


@dataclass
class ConversationContext:
    """Context data stored during conversation."""

    # Customer preferences
    bike_type: Optional[str] = None
    budget: Optional[int] = None
    intended_use: List[str] = field(default_factory=list)

    # Shown products (to avoid repetition)
    shown_product_ids: List[int] = field(default_factory=list)

    # Lead information
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None

    # Recommended products
    recommended_products: List[Dict] = field(default_factory=list)


@dataclass
class ConversationSession:
    """Conversation session data."""

    id: str
    state: ConversationState
    context: ConversationContext
    messages: List[Dict[str, str]]
    created_at: datetime
    last_active: datetime

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.messages.append({"role": role, "content": content})
        self.last_active = datetime.utcnow()

    def update_state(self, new_state: ConversationState) -> None:
        """Update conversation state.

        Args:
            new_state: New state to transition to
        """
        self.state = new_state
        self.last_active = datetime.utcnow()

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if session has expired.

        Args:
            ttl_seconds: Time-to-live in seconds

        Returns:
            True if expired, False otherwise
        """
        age = (datetime.utcnow() - self.last_active).total_seconds()
        return age > ttl_seconds


class SessionStore:
    """Thread-safe in-memory session store."""

    def __init__(self, ttl_minutes: int = 30):
        """Initialize session store.

        Args:
            ttl_minutes: Session time-to-live in minutes
        """
        self._sessions: Dict[str, ConversationSession] = {}
        self._lock = Lock()
        self.ttl_seconds = ttl_minutes * 60

    def create_session(self) -> ConversationSession:
        """Create a new conversation session.

        Returns:
            New ConversationSession
        """
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        session = ConversationSession(
            id=session_id,
            state=ConversationState.GREETING,
            context=ConversationContext(),
            messages=[],
            created_at=now,
            last_active=now,
        )

        with self._lock:
            self._sessions[session_id] = session

        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            ConversationSession if found, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)

            # Check if expired
            if session and session.is_expired(self.ttl_seconds):
                del self._sessions[session_id]
                return None

            return session

    def update_session(self, session: ConversationSession) -> None:
        """Update an existing session.

        Args:
            session: Updated session object
        """
        with self._lock:
            self._sessions[session.id] = session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def cleanup_expired(self) -> int:
        """Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        with self._lock:
            expired_ids = [
                sid
                for sid, session in self._sessions.items()
                if session.is_expired(self.ttl_seconds)
            ]

            for sid in expired_ids:
                del self._sessions[sid]

            return len(expired_ids)

    def get_session_count(self) -> int:
        """Get total number of active sessions.

        Returns:
            Session count
        """
        with self._lock:
            return len(self._sessions)
