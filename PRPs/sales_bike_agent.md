# Sales Bike Agent - Implementation Plan (PRP)

## Executive Summary

This document outlines a comprehensive implementation plan for a Sales AI Agent API for an online bike shop. The agent will conduct customer consultations, recommend products using RAG and vector search, detect customer interest, collect lead information, and integrate with a CRM system. The solution emphasizes automation, AI best practices (RAG, prompt engineering, vector search), and production readiness (Docker deployment, flexible LLM support).

**Key Objectives:**
- Build a conversational API (REST/WebSocket) for natural customer interactions
- Implement RAG-based product recommendations using vector search
- Automate lead capture and CRM integration
- Support FAQ answering from unstructured text
- Enable deployment with Docker and flexible LLM options (OpenAI)

---

## 1. Requirements Analysis

### 1.1 Core Features

**MUST-HAVE (In Scope):**
1. **Conversation API** - Multi-turn conversational interface via REST or WebSocket
2. **Product Recommendations** - RAG-based bike recommendations from product catalog (15 bikes)
3. **Lead Generation** - Detect interest, collect customer details (name, email, phone), create CRM lead
4. **FAQ Support** - Answer general questions from FAQ knowledge base
5. **Deployment** - Docker containerization for production readiness

**OUT OF SCOPE:**
- Appointment scheduling (explicitly marked as OUT_OF_SCOPE in requirements)

### 1.2 Technical Requirements

**Language & Framework:**
- Python (required)
- REST (FastAPI )
- Async support for scalability

**AI/ML Stack:**
- Vector database: FAISS, Qdrant, or supabase as from my env, Pinecone for product/FAQ embeddings
- LLM: OpenAI GPT-4/3.5-turbo OR HuggingFace models OR local LLMs (Ollama/Llama)
- Embeddings: OpenAI embeddings OR HuggingFace sentence-transformers
- Prompt engineering: Visible, well-documented system prompts

**Data Sources:**
- Product catalog: `/Data/product_catalog.json` (15 bikes with specs)
- FAQ: `/Data/faq.txt` (12 Q&A pairs)
- CRM API: `POST /ctream-crm/api/v1/leads` (name, email, phone)

**Deployment:**
- Docker + Docker Compose
- Environment-based configuration (.env)
- Health checks and logging

### 1.3 Evaluation Criteria

The implementation will be assessed on:
1. Clean API design with proper error handling
2. Correct RAG implementation with vector search
3. Visible and effective prompt engineering
4. Docker deployment readiness
5. Flexibility (API vs local LLM support)
6. Natural conversation flow and context awareness
7. Code quality, maintainability, and testing

---

## 2. Technical Architecture

### 2.1 High-Level Architecture

```
┌─────────────┐
│   Client    │
│ (REST/WS)   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Application         │
│  ┌─────────────────────────────┐   │
│  │   Conversation Manager      │   │
│  │  - Session Management       │   │
│  │  - Context Tracking         │   │
│  │  - State Machine (FSM)      │   │
│  └──────────┬──────────────────┘   │
│             │                       │
│  ┌──────────▼──────────────────┐   │
│  │   Agent Orchestrator        │   │
│  │  - Intent Detection         │   │
│  │  - Action Selection         │   │
│  │  - Response Generation      │   │
│  └──┬───────┬───────┬──────────┘   │
│     │       │       │               │
│  ┌──▼──┐ ┌─▼─┐  ┌──▼──────┐       │
│  │ RAG │ │FAQ│  │  Lead   │       │
│  │Prod │ │RAG│  │Capture  │       │
│  └──┬──┘ └─┬─┘  └──┬──────┘       │
│     │       │       │               │
└─────┼───────┼───────┼───────────────┘
      │       │       │
   ┌──▼──┐ ┌──▼──┐ ┌─▼────┐
   │Vector│ │Vector│ │ CRM  │
   │ DB   │ │ DB  │ │ API  │
   │(Prod)│ │(FAQ)│ └──────┘
   └──────┘ └─────┘
```

### 2.2 Component Breakdown

#### 2.2.1 API Layer (FastAPI)
- **REST Endpoints:**
  - `POST /api/v1/conversations` - Start new conversation
  - `POST /api/v1/conversations/{session_id}/messages` - Send message
  - `GET /api/v1/conversations/{session_id}` - Get conversation history
  - `DELETE /api/v1/conversations/{session_id}` - End conversation
  - `GET /health` - Health check

- **WebSocket Endpoint (Optional Enhancement):**
  - `WS /ws/{session_id}` - Real-time bidirectional communication

- **Request/Response Models:**
  ```python
  class MessageRequest(BaseModel):
      message: str
      session_id: Optional[str] = None

  class MessageResponse(BaseModel):
      session_id: str
      response: str
      products: Optional[List[ProductRecommendation]] = None
      lead_created: bool = False
      timestamp: str
  ```

#### 2.2.2 Conversation Manager
- **Session Management:**
  - In-memory session store (Redis for production)
  - Session expiration (30-60 min idle timeout)
  - Conversation history per session (max 20 turns)

- **State Machine (FSM):**
  ```
  States:
  - GREETING: Initial contact
  - DISCOVERY: Understanding customer needs
  - RECOMMENDATION: Showing products
  - INTEREST_CONFIRMED: Customer shows interest
  - LEAD_COLLECTION: Gathering name/email/phone
  - LEAD_CREATED: Successfully created lead
  - FAQ_MODE: Answering general questions
  ```

- **Context Tracking:**
  - Customer preferences (type, budget, usage)
  - Shown products (avoid repetition)
  - Collected info (name, email, phone)
  - Conversation state

#### 2.2.3 Agent Orchestrator (Core Intelligence)

**Responsibilities:**
1. Intent detection (product inquiry vs FAQ vs lead info)
2. Action selection (search products, answer FAQ, collect lead)
3. Prompt engineering and LLM interaction
4. Response generation

**Prompt Engineering Strategy:**

```python
SYSTEM_PROMPT = """You are a friendly and knowledgeable sales agent for a bike shop.

Your goals:
1. Understand customer needs (bike type, budget, intended use)
2. Recommend bikes from the catalog using RAG-retrieved information
3. Answer general questions from the FAQ
4. Detect when customer shows genuine interest (e.g., "I like this", "How can I order?")
5. Collect customer details (name, email, phone) when interest is confirmed
6. Create a lead in the CRM system

Guidelines:
- Be conversational and helpful
- Ask clarifying questions when needed
- Use retrieved product/FAQ data - don't hallucinate
- Keep responses concise (2-3 sentences)
- When showing products, include name, price, and key features
- After detecting interest, politely ask: "Great! To help you further, may I have your name, email, and phone number?"

Current conversation state: {state}
Customer info collected: {collected_info}
"""
```

**Intent Detection:**
- Use LLM with few-shot examples to classify:
  - `product_inquiry`: Customer wants bike recommendations
  - `faq_question`: General question (delivery, warranty, etc.)
  - `lead_info`: Customer provides personal details
  - `interest_signal`: Customer shows buying intent
  - `chitchat`: Small talk/greetings

#### 2.2.4 RAG Module - Product Recommendations

**Vector Database Setup:**
- Use FAISS (lightweight, local) or Qdrant (production)
- Embed each bike with rich metadata:
  ```python
  product_text = f"""
  {name} - {brand} {type}
  Price: €{price}
  Features: {frame_material} frame, {suspension}, {gears} gears, {brakes}
  Intended Use: {", ".join(intended_use)}
  Specs: {wheel_size}" wheels, {weight_kg}kg
  Color: {color}
  """
  ```

**Retrieval Strategy:**
1. Convert customer query to embedding
2. Semantic search in vector DB (top 3-5 results)
3. Rerank by price/features if budget mentioned
4. Return structured product data to LLM

**Example Flow:**
```
User: "I need a bike for city commuting under €1000"
→ Embed query
→ Vector search returns: Urban Cruiser X (€799), Commuter Flex (€999), Vintage Classic 26 (€599)
→ Filter by budget
→ LLM generates response with product details
```

#### 2.2.5 RAG Module - FAQ Answering

**Vector Database Setup:**
- Separate FAISS/Qdrant collection for FAQ
- Embed each Q&A pair:
  ```python
  faq_text = f"Question: {question}\nAnswer: {answer}"
  ```

**Retrieval Strategy:**
1. Detect FAQ intent (keywords: warranty, delivery, return, repair)
2. Semantic search (top 1-2 results)
3. LLM reformulates answer naturally

**Example Flow:**
```
User: "What's the warranty on electric bikes?"
→ Vector search finds: "All new bikes come with a 2-year warranty... Electric bike batteries and motors are covered for 1 year."
→ LLM responds: "Electric bikes have a 1-year warranty on the battery and motor, while the frame and components are covered for 2 years."
```

#### 2.2.6 Lead Capture Module

**Interest Detection:**
- Keyword matching: "interested", "buy", "order", "purchase", "I like"
- LLM classification with confidence score
- Trigger state transition: RECOMMENDATION → INTEREST_CONFIRMED

**Data Collection FSM:**
```
INTEREST_CONFIRMED → Ask for name
→ NAME_COLLECTED → Ask for email
→ EMAIL_COLLECTED → Ask for phone
→ PHONE_COLLECTED → Create lead
```

**Validation:**
- Email regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- Phone regex: `^\+?[0-9]{7,15}$` (international format)
- Name: non-empty string

**CRM Integration:**
```python
async def create_lead(name: str, email: str, phone: str) -> bool:
    payload = {"name": name, "email": email, "phone": phone}
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CRM_API_URL}/ctream-crm/api/v1/leads",
            json=payload,
            headers={"Authorization": f"Bearer {CRM_API_KEY}"}
        )
        return response.status_code == 201
```

#### 2.2.7 LLM Abstraction Layer

**Flexible LLM Support:**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict], temperature: float) -> str:
        pass

class OpenAIProvider(LLMProvider):
    async def generate(self, messages: List[Dict], temperature: float) -> str:
        # OpenAI API call
        pass

class HuggingFaceProvider(LLMProvider):
    async def generate(self, messages: List[Dict], temperature: float) -> str:
        # HF Inference API
        pass

class LocalLLMProvider(LLMProvider):
    async def generate(self, messages: List[Dict], temperature: float) -> str:
        # Ollama or llama.cpp
        pass
```

**Environment-based selection:**
```python
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # openai|huggingface|local
```

---

## 3. Data Flow & Conversation Examples

### 3.1 Product Recommendation Flow

```
User: "I'm looking for a mountain bike for trail riding"

1. API receives message
2. Conversation Manager updates session context
3. Agent Orchestrator detects intent: product_inquiry
4. RAG Module:
   - Embeds query
   - Vector search returns:
     * Trailblazer 500 (€1499, Full Suspension, Trail/Off-road/Downhill)
     * EcoRide E-MTB (€3799, E-Mountain, Trail/Mountain/Off-road)
     * Downhill Master 9000 (€4999, Carbon, Downhill/Freeride)
5. Agent generates response:
   "Great choice! For trail riding, I recommend the Trailblazer 500 by RockRider (€1499).
    It has full suspension, 29" wheels, and hydraulic disc brakes - perfect for trails.
    If you want electric assistance, the EcoRide E-MTB (€3799) is also excellent.
    What's your budget range?"

6. Response sent with structured product data
```

### 3.2 FAQ Flow

```
User: "How long does delivery take?"

1. API receives message
2. Agent detects intent: faq_question
3. FAQ RAG Module:
   - Vector search finds: "Delivery time is usually 5–7 business days..."
4. Agent responds:
   "Delivery typically takes 5-7 business days for bikes in stock.
    Custom orders may take up to 4 weeks. We ship within the EU."

5. Response sent (no product data)
```

### 3.3 Lead Capture Flow

```
User: "The Trailblazer 500 looks perfect!"

Agent: "Wonderful! To help you with the next steps, may I have your name?"

User: "John Doe"

Agent: "Thanks John! What's your email address?"

User: "john@example.com"

Agent: "Great! And your phone number?"

User: "+491234567890"

Agent (internal):
- Validates email and phone
- Calls CRM API: POST /ctream-crm/api/v1/leads
- Receives 201 Created

Agent: "Perfect, John! I've created your profile and a sales consultant will reach out within 24 hours.
       Is there anything else I can help you with today?"
```

---

## 4. Task Breakdown & Dependencies

### Phase 1: Foundation (8-10 hours)

**Task 1.1: Project Setup (1h)**
- Initialize Python project structure
- Setup virtual environment
- Create `requirements.txt` with dependencies:
  - fastapi, uvicorn, pydantic
  - openai, sentence-transformers
  - faiss-cpu (or qdrant-client)
  - httpx, python-dotenv
  - pytest, pytest-asyncio
- Create `.env.example` and `Dockerfile`
- Setup logging configuration

**Task 1.2: Data Ingestion & Vector DB Setup (2-3h)**
- Create `src/data/loader.py`:
  - Load `product_catalog.json` (validate schema)
  - Parse `faq.txt` into structured Q&A pairs
- Create `src/vector_store/embedder.py`:
  - Initialize embedding model (OpenAI or HuggingFace)
  - Generate embeddings for products
  - Generate embeddings for FAQs
- Create `src/vector_store/faiss_store.py`:
  - Initialize FAISS index (separate for products/FAQ)
  - Implement `add_documents()` and `search()` methods
  - Save/load index from disk
- **Acceptance:** Run `python -m src.data.setup_vector_store` → creates FAISS indices successfully

**Task 1.3: LLM Abstraction Layer (2h)**
- Create `src/llm/base.py` with `LLMProvider` interface
- Implement `src/llm/openai_provider.py` (primary)
- Implement `src/llm/local_provider.py` (Ollama fallback)
- Create factory: `get_llm_provider(provider_name: str) -> LLMProvider`
- **Acceptance:** Unit tests for each provider, successful API calls

**Task 1.4: API Foundation (2-3h)**
- Create `src/api/main.py` with FastAPI app
- Implement REST endpoints:
  - `POST /api/v1/conversations` → returns session_id
  - `POST /api/v1/conversations/{session_id}/messages` → MessageRequest/Response
  - `GET /api/v1/conversations/{session_id}` → conversation history
  - `GET /health` → 200 OK
- Setup CORS middleware
- Add request validation and error handlers
- **Acceptance:** Swagger docs at `/docs`, all endpoints return 200/201

### Phase 2: Core Agent Logic (10-12 hours)

**Task 2.1: Conversation Manager (3h)**
- Create `src/agent/session.py`:
  - `ConversationSession` dataclass (id, state, context, history)
  - `SessionStore` (in-memory dict, thread-safe)
  - Methods: `create_session()`, `get_session()`, `update_session()`, `delete_session()`
- Implement conversation state machine (enum: GREETING, DISCOVERY, etc.)
- Add session expiration logic (TTL = 30 min)
- **Acceptance:** Unit tests for session CRUD, state transitions

**Task 2.2: Prompt Engineering & Intent Detection (3-4h)**
- Create `src/agent/prompts.py`:
  - `SYSTEM_PROMPT` with dynamic state/context injection
  - Few-shot examples for intent classification
  - Response formatting guidelines
- Create `src/agent/intents.py`:
  - `detect_intent(message: str, history: List) -> Intent` using LLM
  - Intent enum: PRODUCT_INQUIRY, FAQ_QUESTION, LEAD_INFO, INTEREST_SIGNAL, CHITCHAT
- **Acceptance:** Test with 10 sample messages, 90%+ accuracy

**Task 2.3: RAG Module - Product Recommendations (3-4h)**
- Create `src/agent/product_rag.py`:
  - `search_products(query: str, top_k: int) -> List[Product]`
  - Semantic search in FAISS
  - Re-ranking logic (price filter, feature matching)
  - Format results for LLM prompt
- Create `src/agent/product_response.py`:
  - `generate_product_recommendation(query, products, context) -> str`
  - LLM call with retrieved products + conversation context
- **Acceptance:** Test queries ("city bike under €1000"), verify top 3 results are relevant

**Task 2.4: RAG Module - FAQ Answering (2h)**
- Create `src/agent/faq_rag.py`:
  - `search_faq(query: str, top_k: int) -> List[FAQEntry]`
  - Semantic search in FAQ FAISS index
- Create `src/agent/faq_response.py`:
  - `generate_faq_answer(query, faq_entries, context) -> str`
  - LLM reformulation of FAQ answer
- **Acceptance:** Test queries ("warranty for ebike"), answer cites FAQ correctly

### Phase 3: Lead Capture & CRM Integration (5-6 hours)

**Task 3.1: Interest Detection (2h)**
- Create `src/agent/interest_detector.py`:
  - `detect_interest(message: str, context: dict) -> bool`
  - Keyword matching + LLM classification
  - Trigger state transition: RECOMMENDATION → INTEREST_CONFIRMED
- Update conversation manager to handle state transition
- **Acceptance:** Test with 10 interest signals, 90%+ detection rate

**Task 3.2: Lead Data Collection (2h)**
- Create `src/agent/lead_collector.py`:
  - FSM for collecting name → email → phone
  - Validation functions: `validate_email()`, `validate_phone()`
  - Extract entities from message using regex or LLM
- Update prompts to ask for missing fields
- **Acceptance:** Test full collection flow, validates bad emails/phones

**Task 3.3: CRM Integration (2h)**
- Create `src/crm/client.py`:
  - `async def create_lead(name, email, phone) -> LeadResponse`
  - HTTP POST to `/ctream-crm/api/v1/leads`
  - Retry logic (3 attempts with exponential backoff)
  - Error handling (400, 401, 500)
- Mock CRM API for testing
- **Acceptance:** Integration test with mock API, 201 response, retry on 500

### Phase 4: Integration & Testing (6-8 hours)

**Task 4.1: Agent Orchestrator (3-4h)**
- Create `src/agent/orchestrator.py`:
  - `async def process_message(session_id, message) -> MessageResponse`
  - Integrates: session manager, intent detection, RAG modules, lead collector, CRM client
  - Main conversation loop:
    1. Load session
    2. Detect intent
    3. Execute action (product search / FAQ / lead collection)
    4. Generate response
    5. Update session state
    6. Return response
- Wire up to API endpoints
- **Acceptance:** End-to-end test of full conversation flow

**Task 4.2: Error Handling & Logging (1-2h)**
- Add structured logging (JSON format)
- Handle errors gracefully:
  - LLM API failures → fallback message
  - Vector DB errors → "Search temporarily unavailable"
  - CRM API failures → "We'll contact you manually"
- Add rate limiting (optional)
- **Acceptance:** Test error scenarios, logs are readable, no crashes

**Task 4.3: Unit & Integration Tests (2-3h)**
- Write unit tests:
  - Vector store search
  - Intent detection
  - Lead validation
  - CRM client (mocked)
- Write integration tests:
  - Full conversation flows (product, FAQ, lead)
  - API endpoints (FastAPI TestClient)
- Target: 70%+ code coverage
- **Acceptance:** `pytest` runs all tests, 0 failures

**Task 4.4: Docker & Deployment (1-2h)**
- Create `Dockerfile`:
  - Base image: python:3.11-slim
  - Install dependencies
  - Copy source code
  - Pre-build FAISS indices (or build on startup)
  - Expose port 8000
- Create `docker-compose.yml`:
  - App service
  - Optional: Qdrant service (if using Qdrant)
  - Environment variables
- Create `scripts/startup.sh`:
  - Build vector indices if not exist
  - Start uvicorn server
- **Acceptance:** `docker-compose up` → app runs, health check passes

### Phase 5: Refinement & Documentation (3-4 hours)

**Task 5.1: Conversation Flow Refinement (1-2h)**
- Test conversations with real users
- Refine prompts for naturalness
- Add conversation starters ("Hi! What type of bike are you looking for?")
- Handle edge cases (user changes topic mid-flow)

**Task 5.2: Documentation (1-2h)**
- README.md:
  - Project overview
  - Setup instructions (local + Docker)
  - API documentation (endpoints, examples)
  - Environment variables
- API_DESIGN.md:
  - Request/response schemas
  - Error codes
- PROMPT_ENGINEERING.md:
  - System prompts
  - Intent classification examples
  - RAG retrieval strategy

**Task 5.3: Demo & Video (Optional, 1h)**
- Create demo script (Postman collection or Python script)
- Record demo video (3-5 min)

---

## 5. Technical Decisions & Rationale

### 5.1 Why FastAPI?
- Native async support (critical for LLM/API calls)
- Automatic OpenAPI docs (good UX for evaluators)
- Built-in request validation (Pydantic)
- WebSocket support for future enhancement

### 5.2 Why FAISS over Qdrant/Pinecone?
- **FAISS (Recommended for MVP):**
  - Lightweight, no external service
  - Fast for 15 products + 12 FAQs
  - Easy Docker deployment
- **Qdrant (Production upgrade):**
  - Better for scale (1000+ products)
  - Built-in filtering, CRUD
  - Hybrid search support

### 5.3 Why State Machine for Conversation?
- Explicit control flow (easier debugging)
- Clear lead collection logic (name → email → phone)
- Prevents hallucinated fields (agent won't create lead without all 3 fields)

### 5.4 Why Separate RAG Indices?
- Products and FAQs have different semantics
- Improves retrieval precision
- Allows different top_k values (products: 3-5, FAQ: 1-2)

### 5.5 Why LLM Abstraction Layer?
- Requirement: "OpenAI, HuggingFace or local LLMs allowed"
- Easy to swap providers (env variable)
- Cost optimization (local LLM for dev/testing)

---

## 6. Testing Strategy

### 6.1 Unit Tests
- **Vector Store:** Test embedding generation, search accuracy
- **Intent Detection:** Test classification with labeled examples
- **Lead Validation:** Test email/phone regex, edge cases
- **CRM Client:** Mock HTTP calls, test retry logic

### 6.2 Integration Tests
- **Product Flow:**
  - User asks for city bike
  - Agent retrieves relevant products
  - Response includes top 3 with prices
- **FAQ Flow:**
  - User asks about warranty
  - Agent retrieves FAQ entry
  - Response cites FAQ correctly
- **Lead Flow:**
  - User shows interest
  - Agent collects name/email/phone
  - CRM API called successfully
  - Agent confirms lead creation

### 6.3 Manual Testing
- Conversation scripts (5-10 scenarios)
- Edge cases:
  - User provides invalid email → agent re-prompts
  - User asks unrelated question → agent politely redirects
  - LLM API fails → graceful error message

### 6.4 Load Testing (Optional)
- `locust` or `k6` to test API under load
- Target: 100 concurrent users, <2s response time

---

## 7. Risks & Mitigation

### 7.1 Risk: LLM Hallucination
- **Impact:** Agent recommends non-existent bikes or incorrect info
- **Mitigation:**
  - Strong system prompt: "Only use retrieved data, don't hallucinate"
  - Structured output validation (product IDs must exist)
  - RAG with high top_k to reduce chance of bad retrieval

### 7.2 Risk: CRM API Unavailable
- **Impact:** Leads not created, lost sales opportunities
- **Mitigation:**
  - Retry logic with exponential backoff
  - Fallback: Save lead to local DB/queue, sync later
  - Inform user: "We've noted your details, a consultant will call you"

### 7.3 Risk: Poor Product Retrieval
- **Impact:** Irrelevant recommendations, poor UX
- **Mitigation:**
  - Tune embedding model (test OpenAI vs sentence-transformers)
  - Add metadata filtering (price range, bike type)
  - Re-ranking with business rules (prioritize in-stock, popular bikes)

### 7.4 Risk: Context Loss in Long Conversations
- **Impact:** Agent forgets earlier preferences
- **Mitigation:**
  - Store structured context (budget, type, usage) separately
  - Include summary in LLM prompt: "User wants: mountain bike, €1500 budget, trail riding"
  - Max conversation length: 20 turns (force restart)

### 7.5 Risk: Docker Build Issues
- **Impact:** Evaluators can't run the project
- **Mitigation:**
  - Test Docker build on clean machine
  - Pin all dependency versions
  - Include troubleshooting section in README
  - Provide pre-built Docker image (optional)

---

## 8. Open Questions & Assumptions

### 8.1 Open Questions
1. **CRM API Details:**
   - What's the actual CRM API URL? (Assumed: configurable via env)
   - Authentication method? (Assumed: Bearer token or API key)
   - Expected response format? (Assumed: 201 with lead_id)

2. **Lead Qualification:**
   - Should we validate interest strength? (e.g., "maybe" vs "definitely")
   - Should we recommend specific bike before collecting lead? (Assumed: yes)

3. **WebSocket vs REST:**
   - Is real-time chat required? (Assumed: REST is sufficient, WebSocket optional)

4. **Deployment Target:**
   - Where will this run? (AWS, GCP, on-prem?) (Assumed: generic Docker deployment)

### 8.2 Assumptions
1. **Data:**
   - Product catalog is static (no real-time inventory updates)
   - FAQ is complete (no need to say "I don't know")

2. **Conversation:**
   - English only (no i18n required)
   - Single customer per session (no multi-user support)

3. **Scale:**
   - MVP supports <100 concurrent users
   - FAISS sufficient for 15 products + 12 FAQs

4. **LLM:**
   - OpenAI GPT-4 is primary (fallback to GPT-3.5-turbo or local Llama)
   - Budget: ~$0.01 per conversation (10 turns * 500 tokens avg)

---

## 9. Success Criteria

### 9.1 Functional Requirements
- [ ] API accepts messages and returns responses
- [ ] Agent recommends relevant bikes from catalog
- [ ] Agent answers FAQ questions accurately
- [ ] Agent detects interest and collects name/email/phone
- [ ] CRM lead created successfully with valid data
- [ ] Conversation maintains context across 5+ turns

### 9.2 Non-Functional Requirements
- [ ] API response time: <2s (95th percentile)
- [ ] RAG retrieval accuracy: >80% (top 3 products relevant)
- [ ] Lead collection success rate: >90% (valid data)
- [ ] Docker deployment works on Linux/Mac/Windows
- [ ] Code coverage: >70%
- [ ] No hardcoded credentials (all via .env)

### 9.3 Evaluation Criteria
- [ ] Clean API design (RESTful, proper status codes)
- [ ] RAG correctly implemented (embeddings, vector search, retrieval)
- [ ] Visible prompt engineering (documented system prompts)
- [ ] Flexible LLM support (env-based provider selection)
- [ ] Natural conversation flow (tested with sample dialogs)
- [ ] Code quality (linting, type hints, clear structure)
- [ ] Docker deployment (one-command setup)

---

## 10. Project Structure

```
sales_bike/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, endpoints
│   │   ├── models.py            # Pydantic request/response models
│   │   └── middleware.py        # CORS, logging, error handlers
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main conversation loop
│   │   ├── session.py           # Session management, state machine
│   │   ├── prompts.py           # System prompts, few-shot examples
│   │   ├── intents.py           # Intent detection logic
│   │   ├── product_rag.py       # Product search & recommendation
│   │   ├── faq_rag.py           # FAQ search & answering
│   │   ├── interest_detector.py # Interest signal detection
│   │   └── lead_collector.py    # Lead data collection FSM
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py              # LLMProvider interface
│   │   ├── openai_provider.py   # OpenAI implementation
│   │   ├── local_provider.py    # Local LLM (Ollama)
│   │   └── factory.py           # Provider factory
│   ├── vector_store/
│   │   ├── __init__.py
│   │   ├── embedder.py          # Embedding generation
│   │   ├── faiss_store.py       # FAISS wrapper
│   │   └── models.py            # Product, FAQ dataclasses
│   ├── crm/
│   │   ├── __init__.py
│   │   └── client.py            # CRM API client
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py            # Load product_catalog.json, faq.txt
│   │   └── setup_vector_store.py # Build FAISS indices
│   └── config.py                # Environment config, constants
├── tests/
│   ├── unit/
│   │   ├── test_intents.py
│   │   ├── test_lead_collector.py
│   │   ├── test_vector_store.py
│   │   └── test_crm_client.py
│   ├── integration/
│   │   ├── test_product_flow.py
│   │   ├── test_faq_flow.py
│   │   └── test_lead_flow.py
│   └── conftest.py              # Pytest fixtures
├── data/
│   ├── product_catalog.json
│   ├── faq.txt
│   └── indices/                 # FAISS indices (generated)
├── scripts/
│   ├── setup_env.sh             # Create .env, download models
│   └── startup.sh               # Docker entrypoint
├── docs/
│   ├── API_DESIGN.md
│   ├── PROMPT_ENGINEERING.md
│   └── DEPLOYMENT.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── pyproject.toml               # Optional: for Poetry
```

---

## 11. Dependencies (requirements.txt)

```txt
# API Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-multipart==0.0.6

# LLM & Embeddings
openai==1.10.0
sentence-transformers==2.3.1
tiktoken==0.5.2

# Vector Store
faiss-cpu==1.7.4
# Alternative: qdrant-client==1.7.1

# HTTP Client
httpx==0.26.0

# Utilities
python-dotenv==1.0.0
pydantic-settings==2.1.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0  # for TestClient

# Optional: Local LLM
# llama-cpp-python==0.2.27

# Code Quality
ruff==0.1.13
mypy==1.8.0
```

---

## 12. Estimated Effort

| Phase | Tasks | Hours |
|-------|-------|-------|
| Phase 1: Foundation | 4 tasks | 8-10h |
| Phase 2: Core Agent Logic | 4 tasks | 10-12h |
| Phase 3: Lead Capture & CRM | 3 tasks | 5-6h |
| Phase 4: Integration & Testing | 4 tasks | 6-8h |
| Phase 5: Refinement & Docs | 3 tasks | 3-4h |
| **Total** | **18 tasks** | **32-40h** |

**Team Size:** 1 developer (solo project)
**Timeline:** 1-2 weeks (assuming 4-6h/day)

---

## 13. Next Steps

### Immediate Actions (Week 1)
1. **Environment Setup:**
   - Clone repo, create virtual environment
   - Install dependencies, setup OpenAI API key
   - Test LLM and embedding models

2. **Data Preparation:**
   - Run `setup_vector_store.py` to build FAISS indices
   - Verify product and FAQ embeddings

3. **API Foundation:**
   - Implement FastAPI endpoints
   - Test with Postman or `httpx`

4. **Core Agent:**
   - Implement intent detection
   - Integrate RAG modules
   - Test product recommendations

### Follow-Up Actions (Week 2)
5. **Lead Capture:**
   - Implement interest detection
   - Build lead collection FSM
   - Mock CRM API for testing

6. **Integration:**
   - Wire up agent orchestrator
   - End-to-end testing

7. **Deployment:**
   - Build Docker image
   - Test with `docker-compose up`

8. **Documentation:**
   - Write README, API docs
   - Record demo (optional)

### Pre-Submission Checklist
- [ ] All API endpoints work (test with Postman)
- [ ] Docker deployment successful
- [ ] Unit + integration tests pass
- [ ] README has clear setup instructions
- [ ] Prompts documented in `PROMPT_ENGINEERING.md`
- [ ] Code quality: linted, type-hinted, commented
- [ ] Sample conversation logs included (demonstrate flow)

---

## 14. Contact & Support

**Questions or blockers?**
- Check FAQ in docs/
- Review sample conversations in tests/integration/
- Raise issue in project tracker

**Evaluation Focus:**
- API design & error handling
- RAG implementation (vector search, retrieval quality)
- Prompt engineering (visible in `prompts.py`)
- Docker deployment (one-command setup)
- Conversation naturalness (test with real dialogs)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-13
**Author:** Sales Bike Agent Team
**Status:** Ready for Implementation
