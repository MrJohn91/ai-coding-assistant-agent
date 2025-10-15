# Implementation Plan: Pydantic AI + Mem0 Refactor

**Created**: 2025-10-14
**Status**: Ready for execution
**Requirements Source**: PRPs/requirements-pydantic-mem0-refactor.md

## Executive Summary

This plan refactors the Sales Bike Agent to use **Pydantic AI** for agent structure and **Mem0** for conversation memory. Research was conducted by searching curated Pydantic AI and Mem0 documentation in the Archon knowledge base.

## Research Findings

### From Pydantic AI Documentation (Searched in Archon)

**Sources Searched**:
- `rag_search_knowledge_base(query="agent dependencies tools", source_id="src_pydantic_ai_docs")`
- `rag_read_full_page(page_id="aeb96ee5-a21e-4353-a7b6-1ddd5fe4bc40")` - Dependencies doc
- `rag_read_full_page(page_id="641e75b1-6e6c-4ed1-a5d8-065e7d4d7cc0")` - Weather Agent example

**Key Patterns Learned**:

1. **Dependency Injection Pattern**:
```python
from dataclasses import dataclass
from pydantic_ai import Agent, RunContext

@dataclass
class MyDeps:
    api_key: str
    http_client: httpx.AsyncClient

agent = Agent('openai:gpt-4o', deps_type=MyDeps)
```

2. **Tool Definition Pattern**:
```python
@agent.tool
async def get_weather(ctx: RunContext[Deps], lat: float, lng: float) -> dict:
    # Access dependencies via ctx.deps
    response = await ctx.deps.http_client.get(...)
    return {'temperature': '...', 'description': '...'}
```

3. **System Prompt with Dependencies**:
```python
@agent.system_prompt
async def get_system_prompt(ctx: RunContext[Deps]) -> str:
    # Can access deps in system prompt too
    return f'You are a helpful assistant with API key: {ctx.deps.api_key[:8]}...'
```

### From Mem0 Documentation (Searched in Archon)

**Sources Searched**:
- `rag_search_knowledge_base(query="memory user preferences store", source_id="src_mem0_docs")`
- `rag_read_full_page(page_id="e15ed917-c80f-4a1a-bdd5-63c1016e7ab9")` - Four lines of code
- `rag_read_full_page(page_id="c2aac6a5-f805-4ed1-b81e-dde51b3ba63e")` - Memory in agents

**Key Patterns Learned**:

1. **Memory Initialization**:
```python
from mem0 import MemoryClient

client = MemoryClient(api_key="your-api-key")
```

2. **Adding Conversation History**:
```python
messages = [
    {"role": "user", "content": "Hi, I'm Michael. I prefer mountain bikes."},
    {"role": "assistant", "content": "Nice to meet you Michael!"}
]
client.add(messages, user_id="michael", output_format="v1.0")
```

3. **Searching Memories**:
```python
memories = client.search("What bikes does Michael like?", user_id="michael")
# Returns relevant memories about Michael's preferences
```

4. **Key Concept: Memory ≠ Context Window**:
- Memory is persistent across sessions
- Memory is hierarchical (working, factual, episodic, semantic)
- Memory is low-cost compared to long context windows

5. **Key Concept: Memory ≠ RAG**:
- RAG brings external knowledge (our product catalog)
- Memory brings continuity and learning (customer preferences)

## Architecture Design

### Current Architecture (Before Refactor)

```
User Request
    ↓
FastAPI Endpoint (/chat)
    ↓
AgentOrchestrator
    ├── ProductRAG (Archon MCP) ✅ Good
    ├── FAQRAG (Archon MCP) ✅ Good
    └── OpenAI LLM (direct calls) ❌ Not using Pydantic AI

No conversation memory ❌
```

### Target Architecture (After Refactor)

```
User Request
    ↓
FastAPI Endpoint (/chat)
    ↓
SalesBikeAgent (Pydantic AI Agent)
    ├── Dependencies (via deps_type):
    │   ├── mcp_client (Archon)
    │   ├── memory_client (Mem0)
    │   ├── crm_client
    │   └── session_store
    ├── Tools (via @agent.tool):
    │   ├── @search_products → ProductRAG (Archon)
    │   ├── @search_faq → FAQRAG (Archon)
    │   ├── @recall_customer → Mem0 search
    │   └── @capture_lead → CRM + Mem0 add
    └── System Prompt (via @agent.system_prompt):
        └── Load customer memories from Mem0
```

### Data Flow Example

**Scenario**: Returning customer asks "I need a bike for trails"

```
1. User: "I need a bike for trails"
   ↓
2. SalesBikeAgent receives message
   ↓
3. System prompt function:
   - Searches Mem0: "What does this customer like?"
   - Finds: "Previously interested in Trailblazer 500, prefers under €2000"
   ↓
4. Agent calls @search_products tool:
   - Uses RunContext[Deps] to access mcp_client
   - Searches Archon: "mountain bike trail"
   - Filters by budget €2000 (from memory)
   ↓
5. Agent generates response using:
   - Product results from Archon
   - Customer preferences from Mem0
   ↓
6. After response, agent stores to Mem0:
   - "Customer asked about trail bikes again"
   - "Still interested in mountain bikes"
```

## Task Breakdown

### Task 1: Create Pydantic AI Dependencies Structure

**Effort**: 1-2 hours
**Dependencies**: None
**Files**: New file `src/agent/dependencies.py`

**Implementation**:
```python
from dataclasses import dataclass
from typing import Any
import httpx
from mem0 import MemoryClient

@dataclass
class SalesBikeAgentDeps:
    """Dependencies for Sales Bike Agent (Pydantic AI pattern)."""

    # Archon MCP for product/FAQ search
    mcp_client: Any

    # Mem0 for conversation memory
    memory_client: MemoryClient

    # Existing dependencies
    crm_client: Any
    session_store: Any

    # HTTP client for async requests
    http_client: httpx.AsyncClient
```

**Success Criteria**:
- Dependencies defined as dataclass
- All current dependencies preserved
- New Mem0 client added
- Follows Pydantic AI pattern from docs

---

### Task 2: Refactor ProductRAG as Pydantic AI Tool

**Effort**: 2-3 hours
**Dependencies**: Task 1
**Files**: `src/agent/orchestrator.py` (refactor)

**Implementation**:
```python
from pydantic_ai import Agent, RunContext
from src.agent.dependencies import SalesBikeAgentDeps

sales_agent = Agent(
    'openai:gpt-4o',
    deps_type=SalesBikeAgentDeps,
    retries=2
)

@sales_agent.tool
async def search_products(
    ctx: RunContext[SalesBikeAgentDeps],
    query: str,
    max_price: float | None = None,
    top_k: int = 5
) -> list[dict]:
    """Search for bike products using Archon RAG.

    Based on Pydantic AI tool pattern from documentation.
    """
    # Build search query (2-5 keywords)
    search_query = _extract_keywords(query)

    # Search Archon knowledge base
    result = await ctx.deps.mcp_client.call_tool(
        "mcp__archon__rag_search_knowledge_base",
        arguments={
            "query": search_query,
            "source_id": "file_product_catalog_txt_0b304df3",
            "match_count": top_k * 2
        }
    )

    # Parse and filter results
    products = _parse_products(result)
    if max_price:
        products = [p for p in products if p.get('price', 0) <= max_price]

    return products[:top_k]
```

**Success Criteria**:
- Tool uses `@agent.tool` decorator
- Accesses mcp_client via `ctx.deps`
- Maintains existing Archon RAG integration
- Returns structured product data

---

### Task 3: Refactor FAQRAG as Pydantic AI Tool

**Effort**: 1-2 hours
**Dependencies**: Task 1
**Files**: `src/agent/orchestrator.py` (refactor)

**Implementation**:
```python
@sales_agent.tool
async def search_faq(
    ctx: RunContext[SalesBikeAgentDeps],
    query: str,
    top_k: int = 2
) -> list[dict]:
    """Search FAQ knowledge base using Archon RAG.

    Based on Pydantic AI tool pattern from documentation.
    """
    # Extract FAQ keywords
    search_query = _extract_faq_keywords(query)

    # Search Archon FAQ source
    result = await ctx.deps.mcp_client.call_tool(
        "mcp__archon__rag_search_knowledge_base",
        arguments={
            "query": search_query,
            "source_id": "file_faq_txt_09c5606e",
            "match_count": top_k
        }
    )

    # Parse Q&A format
    faqs = _parse_faqs(result)
    return faqs
```

**Success Criteria**:
- Tool uses `@agent.tool` decorator
- Accesses mcp_client via `ctx.deps`
- Maintains existing Archon RAG integration
- Returns structured FAQ data

---

### Task 4: Add Mem0 Memory Client Setup

**Effort**: 1-2 hours
**Dependencies**: Task 1
**Files**: `src/config.py`, `src/api/main.py`

**Implementation**:

In `src/config.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Mem0 Configuration
    mem0_api_key: str = Field(..., description="Mem0 API key for conversation memory")

    class Config:
        env_file = ".env"
```

In `src/api/main.py`:
```python
from mem0 import MemoryClient
import httpx

@app.on_event("startup")
async def startup_event():
    # ... existing startup code ...

    # Initialize Mem0 client (from documentation pattern)
    memory_client = MemoryClient(api_key=settings.mem0_api_key)
    app.state.memory_client = memory_client

    # Initialize HTTP client for async requests
    app.state.http_client = httpx.AsyncClient()
```

**Success Criteria**:
- Mem0 client initialized following docs pattern
- API key loaded from environment
- Client available in app.state

---

### Task 5: Add Memory Recall Tool

**Effort**: 2-3 hours
**Dependencies**: Task 4
**Files**: `src/agent/orchestrator.py`

**Implementation**:
```python
@sales_agent.tool
async def recall_customer_preferences(
    ctx: RunContext[SalesBikeAgentDeps],
    user_id: str
) -> dict:
    """Recall customer preferences and conversation history from Mem0.

    Based on Mem0 search pattern from documentation.
    """
    try:
        # Search memories (from Mem0 docs)
        memories = ctx.deps.memory_client.search(
            "What are this customer's bike preferences and past interactions?",
            user_id=user_id
        )

        return {
            "has_history": len(memories) > 0,
            "preferences": memories,
            "summary": _summarize_memories(memories)
        }
    except Exception as e:
        # Graceful fallback for new customers
        return {
            "has_history": False,
            "preferences": [],
            "summary": "New customer, no previous history"
        }
```

**Success Criteria**:
- Uses Mem0 `search()` API from documentation
- Returns customer preferences
- Gracefully handles new customers
- Tool available to agent

---

### Task 6: Add Memory Storage on Conversation End

**Effort**: 2-3 hours
**Dependencies**: Task 4
**Files**: `src/agent/orchestrator.py`

**Implementation**:
```python
@sales_agent.tool
async def save_conversation_memory(
    ctx: RunContext[SalesBikeAgentDeps],
    user_id: str,
    conversation_messages: list[dict]
) -> dict:
    """Save conversation to Mem0 for future recall.

    Based on Mem0 add() pattern from documentation.
    """
    try:
        # Add conversation history (from Mem0 docs)
        result = ctx.deps.memory_client.add(
            conversation_messages,
            user_id=user_id,
            output_format="v1.0"
        )

        return {
            "success": True,
            "memories_stored": len(result) if result else 0
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

**Success Criteria**:
- Uses Mem0 `add()` API from documentation
- Stores conversation history
- Returns success status
- Error handling for API failures

---

### Task 7: Update System Prompt with Memory Context

**Effort**: 1-2 hours
**Dependencies**: Task 5
**Files**: `src/agent/orchestrator.py`

**Implementation**:
```python
@sales_agent.system_prompt
async def get_system_prompt(ctx: RunContext[SalesBikeAgentDeps]) -> str:
    """Generate system prompt with customer memory context.

    Based on Pydantic AI system_prompt pattern from documentation.
    """
    # Get session info
    session_id = ctx.usage.get('session_id')
    session = ctx.deps.session_store.get(session_id)

    # Try to recall customer memories
    memories = None
    if session and session.get('user_id'):
        memories = await recall_customer_preferences(
            ctx,
            user_id=session['user_id']
        )

    # Build prompt with memory context
    base_prompt = """You are a friendly bike shop sales assistant.
Your goal is to help customers find the perfect bike."""

    if memories and memories.get('has_history'):
        memory_context = f"\n\nCustomer History:\n{memories['summary']}"
        return base_prompt + memory_context

    return base_prompt
```

**Success Criteria**:
- Uses `@agent.system_prompt` decorator
- Accesses dependencies via `ctx.deps`
- Includes memory context when available
- Graceful fallback for new customers

---

### Task 8: Update FastAPI Endpoint to Use Pydantic AI Agent

**Effort**: 2-3 hours
**Dependencies**: Tasks 1-7
**Files**: `src/api/main.py`

**Implementation**:
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Build dependencies
    deps = SalesBikeAgentDeps(
        mcp_client=app.state.mcp_client,
        memory_client=app.state.memory_client,
        crm_client=app.state.crm_client,
        session_store=app.state.session_store,
        http_client=app.state.http_client
    )

    # Run agent with dependencies
    result = await sales_agent.run(
        request.message,
        deps=deps,
        usage={'session_id': request.session_id}
    )

    # Save conversation to Mem0
    if request.session_id:
        session = app.state.session_store.get(request.session_id)
        if session and session.get('user_id'):
            await save_conversation_memory(
                RunContext(deps=deps),
                user_id=session['user_id'],
                conversation_messages=[
                    {"role": "user", "content": request.message},
                    {"role": "assistant", "content": result.data}
                ]
            )

    return ChatResponse(
        response=result.data,
        session_id=request.session_id,
        products=result.usage.get('products', [])
    )
```

**Success Criteria**:
- Uses Pydantic AI `agent.run()` API
- Passes dependencies correctly
- Saves conversation to Mem0
- Maintains existing API contract

---

### Task 9: Write Tests for Pydantic AI Integration

**Effort**: 2-3 hours
**Dependencies**: Task 8
**Files**: New `tests/test_pydantic_ai_agent.py`

**Test Cases**:
1. Test agent initialization with dependencies
2. Test `search_products` tool with mocked Archon MCP
3. Test `search_faq` tool with mocked Archon MCP
4. Test tool access to dependencies via `ctx.deps`
5. Test error handling when tools fail

**Example**:
```python
import pytest
from pydantic_ai import Agent, RunContext
from src.agent.dependencies import SalesBikeAgentDeps
from src.agent.orchestrator import sales_agent

@pytest.mark.asyncio
async def test_search_products_tool(mock_mcp_client):
    """Test product search tool uses Archon correctly."""
    deps = SalesBikeAgentDeps(
        mcp_client=mock_mcp_client,
        memory_client=Mock(),
        crm_client=Mock(),
        session_store=Mock(),
        http_client=Mock()
    )

    result = await sales_agent.run(
        "I need a mountain bike",
        deps=deps
    )

    # Verify Archon was called
    mock_mcp_client.call_tool.assert_called_with(
        "mcp__archon__rag_search_knowledge_base",
        arguments={
            "query": "mountain bike",
            "source_id": "file_product_catalog_txt_0b304df3",
            "match_count": pytest.approx(10)
        }
    )
```

**Success Criteria**:
- All tests pass
- Tools properly access dependencies
- Mocking works correctly
- Error cases handled

---

### Task 10: Write Tests for Mem0 Integration

**Effort**: 2-3 hours
**Dependencies**: Tasks 5-6
**Files**: New `tests/test_mem0_memory.py`

**Test Cases**:
1. Test memory storage after conversation
2. Test memory recall for returning customer
3. Test graceful handling of new customer (no memories)
4. Test memory-enhanced recommendations
5. Test Mem0 API failures

**Example**:
```python
import pytest
from mem0 import MemoryClient
from src.agent.orchestrator import recall_customer_preferences

@pytest.mark.asyncio
async def test_recall_customer_preferences(mock_memory_client):
    """Test customer preference recall from Mem0."""
    mock_memory_client.search.return_value = [
        {"text": "Customer prefers mountain bikes"},
        {"text": "Budget is under €2000"}
    ]

    deps = SalesBikeAgentDeps(
        memory_client=mock_memory_client,
        # ... other deps ...
    )

    memories = await recall_customer_preferences(
        RunContext(deps=deps),
        user_id="customer-123"
    )

    assert memories['has_history'] is True
    assert len(memories['preferences']) == 2
    assert "mountain bikes" in memories['summary'].lower()
```

**Success Criteria**:
- All tests pass
- Memory storage verified
- Memory recall verified
- Error handling tested

---

### Task 11: Update Documentation

**Effort**: 1-2 hours
**Dependencies**: Task 10
**Files**: `README.md`, `WHY_ARCHON.md`

**Updates Needed**:

1. **README.md** - Add Pydantic AI and Mem0 sections:
```markdown
## Architecture

### Pydantic AI Agent Structure
The Sales Bike Agent uses Pydantic AI for type-safe agent development:
- Dependencies injected via `deps_type` parameter
- Tools defined with `@agent.tool` decorator
- System prompts with `@agent.system_prompt`

### Mem0 Conversation Memory
Customer preferences and history stored with Mem0:
- Persistent memory across sessions
- Personalized recommendations based on history
- Hierarchical memory (working, factual, episodic)

### Archon RAG Integration
Product catalog and FAQ search via Archon MCP:
- Curated knowledge sources (not random web search)
- Vector search with `rag_search_knowledge_base()`
```

2. **WHY_ARCHON.md** - Update to show we used all three doc sources:
```markdown
## How We Actually Used Archon's Curated Docs

We searched THREE documentation sources in Archon during development:

1. **Pydantic AI Docs** (`src_pydantic_ai_docs`)
   - Searched: "agent dependencies tools"
   - Learned: Dependency injection pattern with `deps_type`
   - Applied: Created `SalesBikeAgentDeps` dataclass

2. **Mem0 Docs** (`src_mem0_docs`)
   - Searched: "memory user preferences store"
   - Learned: `MemoryClient` API for add/search
   - Applied: Added conversation memory across sessions

3. **Product/FAQ Data** (`file_product_catalog_txt_*`)
   - Continued using Archon RAG for product search
   - All recommendations grounded in our actual catalog
```

**Success Criteria**:
- README shows Pydantic AI usage
- README shows Mem0 usage
- WHY_ARCHON.md updated with proof we used docs
- Code comments reference doc patterns

---

## Testing Strategy

### Unit Tests
- Test each tool in isolation with mocked dependencies
- Test memory storage/recall functions
- Test dependency injection setup

### Integration Tests
- Test full conversation flow with Pydantic AI agent
- Test memory persistence across multiple sessions
- Test Archon RAG still works with new structure

### E2E Tests
- Test returning customer gets personalized recommendations
- Test new customer conversation gets saved to Mem0
- Test memory + RAG work together

## Success Criteria

### Pydantic AI Integration ✅
- [ ] Agent uses `Agent('openai:gpt-4o', deps_type=SalesBikeAgentDeps)`
- [ ] Dependencies accessed via `RunContext[SalesBikeAgentDeps]`
- [ ] Tools defined with `@agent.tool` decorator
- [ ] System prompt uses `@agent.system_prompt` decorator
- [ ] Type-safe throughout

### Mem0 Integration ✅
- [ ] `MemoryClient` initialized from config
- [ ] Conversations saved with `client.add(messages, user_id=...)`
- [ ] Memories recalled with `client.search(query, user_id=...)`
- [ ] Personalized recommendations based on history
- [ ] Graceful handling of new customers

### Archon RAG Maintained ✅
- [ ] Product search still uses Archon MCP
- [ ] FAQ search still uses Archon MCP
- [ ] No regression in search quality

### Documentation ✅
- [ ] README shows Pydantic AI and Mem0 usage
- [ ] WHY_ARCHON.md proves we searched docs in Archon
- [ ] Code comments reference doc patterns
- [ ] Examples of memory-enhanced conversations

### Process Followed ✅
- [x] Used `/create-plan` to research first
- [x] Searched Pydantic AI docs in Archon
- [x] Searched Mem0 docs in Archon
- [ ] Will use `/execute-plan` for implementation
- [ ] Will track tasks in Archon project

## Risks and Mitigation

### Risk 1: Mem0 API Key Required
**Mitigation**: Document setup clearly, provide .env.example

### Risk 2: Breaking Existing Tests
**Mitigation**: Refactor incrementally, run tests after each task

### Risk 3: Mem0 API Failures
**Mitigation**: Graceful fallbacks for memory operations

### Risk 4: Performance Impact
**Mitigation**: Add memory recall only when beneficial, cache where possible

## Technical Constraints

✅ **Keep FastAPI backend** - Just update endpoint to use Pydantic AI agent
✅ **Keep Archon MCP** - Continue using for product/FAQ search
✅ **Keep existing API contract** - ChatRequest/ChatResponse unchanged
✅ **Backward compatible** - Old sessions continue working

## Out of Scope

❌ Complete API rewrite
❌ Changing CRM integration
❌ Modifying conversation state machine
❌ Changing Docker deployment

## Next Steps

1. **Review this plan** with user to ensure it matches video workflow expectations
2. **Create tasks in Archon** for tracking (use `manage_task` for each of the 11 tasks)
3. **Run `/execute-plan`** to implement following Archon-first workflow
4. **Validate** that we actually leveraged the curated docs (not just training data)

## References

**Archon Knowledge Base Sources Used**:
- `src_pydantic_ai_docs` - Pydantic AI documentation
- `src_mem0_docs` - Mem0 documentation
- `file_product_catalog_txt_0b304df3` - Our bike products
- `file_faq_txt_09c5606e` - Our FAQ entries

**Specific Pages Read**:
- Pydantic AI Dependencies (page_id: aeb96ee5-a21e-4353-a7b6-1ddd5fe4bc40)
- Pydantic AI Weather Agent (page_id: 641e75b1-6e6c-4ed1-a5d8-065e7d4d7cc0)
- Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)
- Mem0 Memory in Agents (page_id: c2aac6a5-f805-4ed1-b81e-dde51b3ba63e)

**External References**:
- [Cole Medin's Archon Guide](https://www.youtube.com/watch?v=DMXyDpnzNpY)
- [Pydantic AI](https://ai.pydantic.dev/)
- [Mem0](https://docs.mem0.ai/)
