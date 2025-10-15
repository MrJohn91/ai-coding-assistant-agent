"""Agent orchestrator - main conversation loop - Archon MCP version."""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.agent.faq_rag import FAQRAG
from src.agent.interest_detector import detect_interest
from src.agent.intents import Intent, detect_intent
from src.agent.lead_collector import LeadCollector
from src.agent.product_rag import ProductRAG
from src.agent.prompts import LEAD_COLLECTION_PROMPTS, build_system_prompt
from src.agent.session import ConversationSession, ConversationState, SessionStore
from src.api.models import ProductRecommendation
from src.crm.client import CRMClient
from src.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Main orchestrator for agent conversation flow using Archon MCP."""

    def __init__(
        self,
        session_store: SessionStore,
        mcp_client: Any,
        llm: LLMProvider,
        crm_client: CRMClient,
    ):
        """Initialize agent orchestrator with Archon MCP.

        Args:
            session_store: Session store
            mcp_client: Archon MCP client for RAG operations
            llm: LLM provider
            crm_client: CRM client
        """
        self.session_store = session_store
        self.product_rag = ProductRAG(mcp_client, llm)
        self.faq_rag = FAQRAG(mcp_client, llm)
        self.llm = llm
        self.crm_client = crm_client
        self.lead_collector = LeadCollector()

    async def process_message(
        self, session_id: str, message: str
    ) -> Tuple[str, Optional[List[ProductRecommendation]], bool]:
        """Process user message and generate response.

        Args:
            session_id: Conversation session ID
            message: User message

        Returns:
            Tuple of (response, products, lead_created)
        """
        # Load session
        session = self.session_store.get_session(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return ("Session expired. Please start a new conversation.", None, False)

        # Add user message to history
        session.add_message("user", message)

        try:
            # Handle lead collection states first
            if session.state in [
                ConversationState.INTEREST_CONFIRMED,
                ConversationState.NAME_COLLECTED,
                ConversationState.EMAIL_COLLECTED,
                ConversationState.PHONE_COLLECTED,
            ]:
                response, lead_created = await self._handle_lead_collection(session, message)
                self.session_store.update_session(session)
                return response, None, lead_created

            # Detect intent
            intent_result = await detect_intent(message, session.messages, self.llm)
            intent = intent_result["intent"]

            logger.info(f"Session {session_id}: intent={intent.value}, state={session.state.value}")

            # Check for interest signal
            if intent == Intent.INTEREST_SIGNAL or detect_interest(message, session.context.__dict__):
                response = await self._handle_interest_signal(session)
                self.session_store.update_session(session)
                return response, None, False

            # Route based on intent
            if intent == Intent.PRODUCT_INQUIRY:
                response, products = await self._handle_product_inquiry(session, message)
                self.session_store.update_session(session)
                return response, products, False

            elif intent == Intent.FAQ_QUESTION:
                response = await self._handle_faq_question(session, message)
                self.session_store.update_session(session)
                return response, None, False

            elif intent == Intent.LEAD_INFO:
                # User provided info without prompting
                response, lead_created = await self._handle_lead_collection(session, message)
                self.session_store.update_session(session)
                return response, None, lead_created

            else:
                # Chitchat or unclear
                response = await self._handle_chitchat(session, message)
                self.session_store.update_session(session)
                return response, None, False

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            session.add_message("assistant", "I apologize, but I encountered an error. Could you please try again?")
            self.session_store.update_session(session)
            return ("I apologize, but I encountered an error. Could you please try again?", None, False)

    async def _handle_product_inquiry(
        self, session: ConversationSession, message: str
    ) -> Tuple[str, Optional[List[ProductRecommendation]]]:
        """Handle product inquiry.

        Args:
            session: Conversation session
            message: User message

        Returns:
            Tuple of (response, products)
        """
        # Search products
        products = await self.product_rag.search_products(
            message,
            top_k=5,
            max_price=session.context.budget,
        )

        if not products:
            response = "I couldn't find any bikes matching your criteria. Could you tell me more about what you're looking for?"
            session.add_message("assistant", response)
            return response, None

        # Generate recommendation
        response = await self.product_rag.generate_recommendation(
            message,
            products,
            bike_type=session.context.bike_type,
            budget=session.context.budget,
            intended_use=session.context.intended_use,
        )

        # Store shown products
        for product, _ in products[:3]:
            product_id = product.get("id")
            if product_id and product_id not in session.context.shown_product_ids:
                session.context.shown_product_ids.append(product_id)

        # Update context with preferences
        session.context.recommended_products = [
            {"id": p.get("id"), "name": p.get("name"), "price": p.get("price_eur")}
            for p, _ in products[:3]
        ]

        # Update state
        if session.state == ConversationState.GREETING:
            session.update_state(ConversationState.DISCOVERY)

        session.add_message("assistant", response)

        # Convert to API model
        product_recs = [
            ProductRecommendation(
                id=p.get("id", 0),
                name=p.get("name", "Unknown"),
                type=p.get("type", "Bike"),
                brand=p.get("brand", "Unknown"),
                price_eur=p.get("price_eur", 0),
                key_features=f"{p.get('frame_material', 'N/A')} frame, {p.get('gears', 'N/A')} gears, {p.get('brakes', 'N/A')}",
                intended_use=p.get("intended_use", []),
            )
            for p, _ in products[:3]
        ]

        return response, product_recs

    async def _handle_faq_question(
        self, session: ConversationSession, message: str
    ) -> str:
        """Handle FAQ question.

        Args:
            session: Conversation session
            message: User message

        Returns:
            Response text
        """
        # Search FAQ
        faq_entries = await self.faq_rag.search_faq(message, top_k=2)

        # Generate answer
        response = await self.faq_rag.generate_answer(message, faq_entries)

        session.add_message("assistant", response)
        return response

    async def _handle_interest_signal(self, session: ConversationSession) -> str:
        """Handle interest signal - start lead collection.

        Args:
            session: Conversation session

        Returns:
            Response text
        """
        # Transition to lead collection
        session.update_state(ConversationState.INTEREST_CONFIRMED)

        # Ask for name
        response = LEAD_COLLECTION_PROMPTS["ask_name"]
        session.add_message("assistant", response)

        return response

    async def _handle_lead_collection(
        self, session: ConversationSession, message: str
    ) -> Tuple[str, bool]:
        """Handle lead data collection.

        Args:
            session: Conversation session
            message: User message

        Returns:
            Tuple of (response, lead_created)
        """
        # Determine what field we're collecting
        if session.state == ConversationState.INTEREST_CONFIRMED:
            # Collecting name
            name, error = self.lead_collector.extract_lead_info(message, "name")
            if name:
                session.context.customer_name = name
                session.update_state(ConversationState.NAME_COLLECTED)
                response = LEAD_COLLECTION_PROMPTS["ask_email"].format(name=name)
                session.add_message("assistant", response)
                return response, False
            else:
                session.add_message("assistant", error)
                return error, False

        elif session.state == ConversationState.NAME_COLLECTED:
            # Collecting email
            email, error = self.lead_collector.extract_lead_info(message, "email")
            if email:
                session.context.customer_email = email
                session.update_state(ConversationState.EMAIL_COLLECTED)
                response = LEAD_COLLECTION_PROMPTS["ask_phone"]
                session.add_message("assistant", response)
                return response, False
            else:
                session.add_message("assistant", error)
                return error, False

        elif session.state == ConversationState.EMAIL_COLLECTED:
            # Collecting phone
            phone, error = self.lead_collector.extract_lead_info(message, "phone")
            if phone:
                session.context.customer_phone = phone
                session.update_state(ConversationState.PHONE_COLLECTED)

                # Create lead in CRM
                lead_result = await self.crm_client.create_lead(
                    name=session.context.customer_name,
                    email=session.context.customer_email,
                    phone=phone,
                )

                if lead_result.success:
                    session.update_state(ConversationState.LEAD_CREATED)
                    response = LEAD_COLLECTION_PROMPTS["confirm_lead"].format(
                        name=session.context.customer_name
                    )
                    session.add_message("assistant", response)
                    return response, True
                else:
                    # CRM failed, but we have the info
                    response = (
                        f"Thank you, {session.context.customer_name}! "
                        "I've noted your details. A sales consultant will contact you soon."
                    )
                    session.add_message("assistant", response)
                    return response, False
            else:
                session.add_message("assistant", error)
                return error, False

        # Should not reach here
        response = "Let me help you find the perfect bike. What are you looking for?"
        session.add_message("assistant", response)
        return response, False

    async def _handle_chitchat(self, session: ConversationSession, message: str) -> str:
        """Handle chitchat or unclear messages.

        Args:
            session: Conversation session
            message: User message

        Returns:
            Response text
        """
        if session.state == ConversationState.GREETING:
            response = "Hello! I'm here to help you find the perfect bike. What type of bike are you looking for?"
        else:
            response = "I'm here to help you find the perfect bike. Is there anything specific you'd like to know about our bikes or services?"

        session.add_message("assistant", response)
        return response
