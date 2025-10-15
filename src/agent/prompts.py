"""Prompt templates and engineering for the sales agent."""

from src.agent.session import ConversationContext, ConversationState

# System prompt for the sales agent
SYSTEM_PROMPT_TEMPLATE = """You are a friendly and knowledgeable sales agent for an online bike shop.

Your goals:
1. Understand customer needs (bike type, budget, intended use)
2. Recommend bikes from the catalog using RAG-retrieved information
3. Answer general questions from the FAQ knowledge base
4. Detect when customer shows genuine interest (e.g., "I like this", "How can I order?")
5. Collect customer details (name, email, phone) when interest is confirmed
6. Create a lead in the CRM system

Guidelines:
- Be conversational and helpful
- Ask clarifying questions when needed
- Use retrieved product/FAQ data - don't hallucinate
- Keep responses concise (2-3 sentences)
- When showing products, include name, price, and key features
- After detecting interest, politely ask: "Great! To help you further, may I have your name?"

Current conversation state: {state}
Customer preferences: {preferences}
Customer info collected: {collected_info}
"""

# Intent classification prompt
INTENT_CLASSIFICATION_PROMPT = """Classify the user's intent from their message.

Intent types:
1. PRODUCT_INQUIRY: User wants bike recommendations or asks about bike features
2. FAQ_QUESTION: General question about delivery, warranty, payment, services, etc.
3. LEAD_INFO: User provides personal details (name, email, phone)
4. INTEREST_SIGNAL: User shows buying intent ("I like this", "interested", "want to buy")
5. CHITCHAT: Greeting, small talk, off-topic

User message: "{message}"

Recent context:
{context}

Respond with ONLY the intent type (one of the 5 options above) and a confidence score 0-1.
Format: {{"intent": "INTENT_TYPE", "confidence": 0.95}}
"""

# Few-shot examples for intent classification
INTENT_EXAMPLES = """
Examples:

Message: "I need a mountain bike for trail riding"
Intent: PRODUCT_INQUIRY

Message: "What's the warranty on electric bikes?"
Intent: FAQ_QUESTION

Message: "My name is John Doe"
Intent: LEAD_INFO

Message: "The Trailblazer 500 looks perfect!"
Intent: INTEREST_SIGNAL

Message: "Hello!"
Intent: CHITCHAT

Message: "Do you ship to Austria?"
Intent: FAQ_QUESTION

Message: "I'm interested in the Urban Cruiser"
Intent: INTEREST_SIGNAL

Message: "john@example.com"
Intent: LEAD_INFO
"""

# Product recommendation prompt
PRODUCT_RECOMMENDATION_PROMPT = """Based on the customer's needs, recommend the most suitable bikes from the search results.

Customer query: "{query}"
Customer preferences:
- Type: {bike_type}
- Budget: {budget}
- Intended use: {intended_use}

Retrieved products:
{products}

Provide a natural, conversational response recommending the top 2-3 bikes. Include:
- Product name and price
- Key features that match their needs
- Why it's a good fit

Keep it concise and friendly.
"""

# FAQ answer prompt
FAQ_ANSWER_PROMPT = """Answer the customer's question using the FAQ information provided.

Customer question: "{query}"

Relevant FAQ entries:
{faq_entries}

Provide a natural, helpful answer based on the FAQ. Don't add information not in the FAQ.
Keep it concise (2-3 sentences).
"""

# Lead collection prompts
LEAD_COLLECTION_PROMPTS = {
    "ask_name": "Great! To help you further, may I have your name?",
    "ask_email": "Thanks {name}! What's your email address?",
    "ask_phone": "Perfect! And your phone number?",
    "confirm_lead": "Excellent, {name}! I've created your profile. A sales consultant will reach out to you within 24 hours. Is there anything else I can help you with today?",
}


def build_system_prompt(
    state: ConversationState, context: ConversationContext
) -> str:
    """Build system prompt with current state and context.

    Args:
        state: Current conversation state
        context: Conversation context

    Returns:
        Formatted system prompt
    """
    preferences = []
    if context.bike_type:
        preferences.append(f"Type: {context.bike_type}")
    if context.budget:
        preferences.append(f"Budget: €{context.budget}")
    if context.intended_use:
        preferences.append(f"Use: {', '.join(context.intended_use)}")

    preferences_str = ", ".join(preferences) if preferences else "Not yet determined"

    collected_info = []
    if context.customer_name:
        collected_info.append(f"Name: {context.customer_name}")
    if context.customer_email:
        collected_info.append(f"Email: {context.customer_email}")
    if context.customer_phone:
        collected_info.append(f"Phone: {context.customer_phone}")

    collected_info_str = ", ".join(collected_info) if collected_info else "None"

    return SYSTEM_PROMPT_TEMPLATE.format(
        state=state.value,
        preferences=preferences_str,
        collected_info=collected_info_str,
    )


def build_intent_prompt(message: str, recent_messages: list) -> str:
    """Build intent classification prompt.

    Args:
        message: User message
        recent_messages: Recent conversation messages

    Returns:
        Formatted intent prompt
    """
    # Get last 2 messages for context
    context_lines = []
    for msg in recent_messages[-2:]:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role == "user":
            context_lines.append(f"User: {content}")
        elif role == "assistant":
            context_lines.append(f"Assistant: {content}")

    context_str = "\n".join(context_lines) if context_lines else "No prior context"

    return INTENT_CLASSIFICATION_PROMPT.format(
        message=message,
        context=context_str,
    )
