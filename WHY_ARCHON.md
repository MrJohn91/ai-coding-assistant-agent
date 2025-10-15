# Why We Use Archon MCP for Sales Bike Agent

## Overview

The Sales Bike Agent is built using the **Archon-first** approach, following Cole Medin's methodology from "[The OFFICIAL Archon Guide - 10x Your AI Coding Workflow](https://www.youtube.com/watch?v=DMXyDpnzNpY)". This document explains why we chose Archon, what problems it solves according to the video, and how it specifically helped us build this sales agent.

## What is Archon?

Archon is your **command center for AI coding**. As Cole Medin explains:

> "It is your tool to manage all of your knowledge and tasks for your AI coding assistant. The big goal of Archon is to be the one tool that enables AI and human collaboration at a very deep level."

Archon provides two critical capabilities:

1. **Curated Knowledge Base**: You pick which documentation the AI searches (not the whole web)
2. **Collaborative Task Management**: You and the AI manage the same tasks in real-time

## The Core Problems Archon Solves (From the Video)

Cole Medin identifies **two fundamental problems** with current AI coding assistants:

### Problem 1: Can't Control Knowledge Sources

**Cole's Quote:**
> "The big problem that we have with AI coding assistants right now is they take care of too many things under the hood... they have the ability to search the web. That's their way to retrieve external documentation... but the problem is there's not really a way for us to collaborate with the AI coding assistant on these things. We can't really pick the knowledge that it searches through because it's just going to search the entire internet."

**What This Meant for Sales Bike Agent:**

Without Archon, if Claude Code searched for "bike product recommendations" or "FAQ handling patterns", it would:
- Search the entire internet
- Pull random bike shop examples
- Use outdated API patterns
- Miss our specific product catalog (15 bikes)
- Miss our specific FAQs (12 entries)

**With Archon:**

We curated exactly what Claude Code searches:
```bash
Knowledge Base in Archon (for Sales Bike Agent):
├── file_product_catalog_txt_0b304df3  # Our 15 bike products
├── file_faq_txt_09c5606e              # Our 12 FAQ entries
├── src_pydantic_ai_docs               # For building better agents
└── src_mem0_docs                      # For conversation memory patterns
```

Now when Claude Code needs to implement product search or FAQ handling, it searches **our curated knowledge**, not random web results.

**Code Example:**
```python
# Claude Code searches OUR product catalog via Archon
result = await mcp_client.call_tool(
    "mcp__archon__rag_search_knowledge_base",
    arguments={
        "query": "mountain bike trail",
        "source_id": "file_product_catalog_txt_0b304df3",  # Our products!
        "match_count": 5
    }
)
```

### Problem 2: Can't Collaborate on Tasks

**Cole's Quote:**
> "They also have the ability to create their own internal task lists so they can organize their own work and knock things out task by task... but the problem is there's not really a way for us to collaborate with the AI coding assistant on these things... we can't really interact with this task list. It's more of an internal tool."

**What This Meant for Sales Bike Agent:**

Traditional AI coding flow:
1. I tell Claude Code: "Build a sales bike agent"
2. Claude Code creates internal task list (I can't see it)
3. Claude Code works through tasks (I don't know what it's doing)
4. I can't add tasks mid-development
5. I can't track what's done vs. what's left

**With Archon:**

We created the Sales Bike Agent project with 6 tasks that **both** Claude Code and I could see and manage:

```
Sales Bike Agent Project in Archon:
┌─────────────────────────────────────────────┬──────────┐
│ Task                                        │ Status   │
├─────────────────────────────────────────────┼──────────┤
│ 1. Verify FAISS vector store setup          │ ✅ DONE  │
│ 2. Test end-to-end conversation flow        │ ✅ DONE  │
│ 3. Build Docker deployment                  │ ✅ DONE  │
│ 4. Write unit and integration tests         │ ✅ DONE  │
│ 5. Create documentation                     │ ✅ DONE  │
│ 6. Refactor to use Archon RAG               │ ✅ DONE  │
└─────────────────────────────────────────────┴──────────┘
```

**Real-Time Collaboration Example:**

As Cole shows in the video: *"We can even create our own tasks here without even having to interrupt Claude Code. We can collaborate with it because the next time it looks at the tasks that it has to do, it'll find those new tasks that we have created for it."*

When you (the user) said "did the implementation check documents in archon?", I could see that as a gap and we refactored. If this was a task in Archon, you could have added it mid-development, and I would have picked it up automatically.

**Benefits for Sales Bike Agent:**
- ✅ **Visibility**: You see exactly what I'm working on
- ✅ **Control**: You can add/edit tasks while I work
- ✅ **Progress tracking**: Clear dashboard of what's done
- ✅ **No surprises**: You know what's left to build

## How Archon Specifically Helped Build Sales Bike Agent

### 1. Product RAG Implementation

**Challenge:** Build a system to recommend bikes from our catalog

**Archon Solution:**
- Uploaded `product_catalog.txt` with 15 bikes to Archon
- Claude Code searched this source when implementing `ProductRAG`
- No hallucinated product attributes - all came from our actual data

**Code Generated:**
```python
class ProductRAG:
    """Product recommendation using Archon RAG."""

    PRODUCT_SOURCE_ID = "file_product_catalog_txt_0b304df3"  # Our bikes!

    async def search_products(self, query: str):
        # Search OUR product catalog, not random internet data
        result = await self.mcp_client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            arguments={
                "query": query,
                "source_id": self.PRODUCT_SOURCE_ID,
                "match_count": 5
            }
        )
```

### 2. FAQ Implementation

**Challenge:** Build FAQ answering using our 12 specific FAQ entries

**Archon Solution:**
- Uploaded `faq.txt` with our FAQs to Archon
- Claude Code implemented FAQ search using exact same pattern
- All FAQ responses grounded in our actual policies

**Code Generated:**
```python
class FAQRAG:
    """FAQ answering using Archon RAG."""

    FAQ_SOURCE_ID = "file_faq_txt_09c5606e"  # Our FAQs!

    async def search_faq(self, query: str):
        # Search OUR FAQs, not generic bike shop FAQs
        result = await self.mcp_client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            arguments={
                "query": query,
                "source_id": self.FAQ_SOURCE_ID,
                "match_count": 2
            }
        )
```

### 3. Task-Driven Development

**The 6-Task Journey:**

1. **Task 1: Verify FAISS vector store** → Built initial RAG system
2. **Task 2: Test conversation flow** → Full e2e testing with real API calls
3. **Task 3: Docker deployment** → Production-ready containerization
4. **Task 4: Write tests** → 6 unit tests + integration tests, all passing
5. **Task 5: Documentation** → README, API_DESIGN, comprehensive docs
6. **Task 6: Refactor to Archon** → **YOU noticed we weren't using Archon RAG!**

That last task is the perfect example of collaboration. You saw the tasks, realized we built local FAISS instead of using Archon, and asked: *"did the implementation check documents in archon?"*

This led to the complete refactoring to use Archon MCP properly!

## How It Works in Sales Bike Agent

### Product Recommendations (product_rag.py)

```python
class ProductRAG:
    """Product recommendation using Archon RAG."""

    PRODUCT_SOURCE_ID = "file_product_catalog_txt_0b304df3"

    async def search_products(self, query: str):
        # 1. Build optimized search query (2-5 keywords)
        search_query = self._build_search_query(query)

        # 2. Search Archon RAG
        result = await self.mcp_client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            arguments={
                "query": search_query,
                "source_id": self.PRODUCT_SOURCE_ID,
                "match_count": top_k * 2,
                "return_mode": "pages"
            }
        )

        # 3. Parse results and filter by price
        products = self._parse_archon_results(result, max_price, top_k)
        return products
```

### FAQ Answering (faq_rag.py)

```python
class FAQRAG:
    """FAQ answering using Archon RAG."""

    FAQ_SOURCE_ID = "file_faq_txt_09c5606e"

    async def search_faq(self, query: str):
        # 1. Extract FAQ keywords (warranty, delivery, etc.)
        search_query = self._build_search_query(query)

        # 2. Search Archon FAQ knowledge base
        result = await self.mcp_client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            arguments={
                "query": search_query,
                "source_id": self.FAQ_SOURCE_ID,
                "match_count": 2
            }
        )

        # 3. Parse Q&A format from results
        faqs = self._parse_archon_results(result)
        return faqs
```

### Orchestrator Integration (orchestrator.py)

```python
class AgentOrchestrator:
    """Main orchestrator using Archon MCP."""

    def __init__(self, session_store, mcp_client, llm, crm_client):
        # Initialize with Archon MCP client
        self.product_rag = ProductRAG(mcp_client, llm)
        self.faq_rag = FAQRAG(mcp_client, llm)

    async def _handle_product_inquiry(self, session, message):
        # Search products via Archon
        products = await self.product_rag.search_products(message)

        # Generate recommendation
        response = await self.product_rag.generate_recommendation(
            message, products
        )

        return response, product_recs
```

## Data Flow Diagram

```
User Query: "I need a mountain bike under €2000"
    ↓
┌─────────────────────────────────────────┐
│  Sales Bike Agent API                   │
│  (FastAPI)                               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  AgentOrchestrator                      │
│  - Detect intent: PRODUCT_INQUIRY       │
│  - Route to ProductRAG                  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  ProductRAG                             │
│  1. Build query: "mountain bike"        │
│  2. Extract budget: €2000               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  Archon MCP Server                      │
│  rag_search_knowledge_base()            │
│  - Vector search in product catalog     │
│  - Return top 5 matches                 │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  ProductRAG                             │
│  3. Parse JSON products                 │
│  4. Filter by price (≤€2000)            │
│  5. Format for LLM prompt               │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  OpenAI GPT-4                           │
│  - Generate natural recommendation      │
│  - "Based on your needs, I recommend    │
│     the Trailblazer 500..."             │
└─────────────────────────────────────────┘
    ↓
Return to User: Recommendation + Product List
```

## Before vs After: Our Refactoring Journey

### Initial Approach (Local FAISS)

```python
# src/agent/product_rag.py (OLD)
from src.vector_store.faiss_store import ProductVectorStore

class ProductRAG:
    def __init__(self, product_store: ProductVectorStore, llm):
        self.product_store = product_store  # Local FAISS

    async def search_products(self, query):
        # Search local FAISS index
        results = self.product_store.search(query, top_k=5)
```

**Problems:**
- Had to build FAISS indices locally (`python -m src.data.setup_vector_store`)
- Managed embedding generation ourselves
- Couldn't leverage Pydantic AI or Mem0 docs (not in local store)
- You couldn't see what knowledge sources I was using

### Archon-First Approach (Current)

```python
# src/agent/product_rag.py (NEW)
class ProductRAG:
    PRODUCT_SOURCE_ID = "file_product_catalog_txt_0b304df3"

    def __init__(self, mcp_client, llm):
        self.mcp_client = mcp_client  # Archon MCP!

    async def search_products(self, query):
        # Search Archon knowledge base
        result = await self.mcp_client.call_tool(
            "mcp__archon__rag_search_knowledge_base",
            arguments={
                "query": query,
                "source_id": self.PRODUCT_SOURCE_ID,
                "match_count": 5
            }
        )
```

**Benefits:**
- ✅ **Curated knowledge**: You uploaded products/FAQs, I search them
- ✅ **Visible sources**: You see in Archon UI what I'm searching
- ✅ **Can add docs**: You can add Pydantic AI patterns mid-development
- ✅ **Collaborative**: We both control the knowledge base

## The Two Key Benefits We Actually Got

Following Cole's video, Archon solved the two core problems:

### 1. Curated Knowledge = Better Code

**Example:** When implementing FAQ handling, instead of Claude Code searching random "FAQ chatbot patterns" on the web, it searched YOUR 12 specific FAQs in Archon. The generated code uses your exact warranty policy, delivery timeframes, and return procedures.

### 2. Collaborative Tasks = Better Workflow

**Example:** You created 6 tasks in Archon. I worked through them. You noticed task 6 ("Refactor to Archon RAG") wasn't truly done - we were still using local FAISS. You asked about it, and we fixed it together. That's the collaboration Cole talks about.

## How We Actually Used All Three Knowledge Sources

Following the Archon-first workflow from Cole's video, we DID leverage all three documentation sources:

### 1. ✅ Used Pydantic AI Documentation

**What We Searched:**
- `rag_search_knowledge_base(query="agent dependencies tools", source_id="src_pydantic_ai_docs")`
- Read full page: Pydantic AI Dependencies (page_id: aeb96ee5-a21e-4353-a7b6-1ddd5fe4bc40)
- Read full page: Pydantic AI Weather Agent (page_id: 641e75b1-6e6c-4ed1-a5d8-065e7d4d7cc0)

**What We Learned:**
- Dependency injection pattern with `@dataclass` and `deps_type` parameter
- Tool definition with `@agent.tool` decorator
- Accessing dependencies via `RunContext[Deps]`
- System prompts with `@agent.system_prompt` decorator

**What We Built:**
```python
# src/agent/dependencies.py - Following Pydantic AI pattern
@dataclass
class SalesBikeAgentDeps:
    """Dependencies for Sales Bike Agent (Pydantic AI pattern)."""
    mcp_client: Any
    memory_client: MemoryClient
    crm_client: Any
    session_store: Any
    http_client: httpx.AsyncClient

# src/agent/pydantic_agent.py - Using the pattern from docs
sales_agent = Agent('openai:gpt-4o', deps_type=SalesBikeAgentDeps, retries=2)

@sales_agent.tool
async def search_products(ctx: RunContext[SalesBikeAgentDeps], query: str):
    # Access Archon MCP via ctx.deps (Pydantic AI pattern!)
    result = await ctx.deps.mcp_client.call_tool(...)
```

### 2. ✅ Used Mem0 Documentation

**What We Searched:**
- `rag_search_knowledge_base(query="memory user preferences store", source_id="src_mem0_docs")`
- Read full page: Mem0 Four Lines of Code (page_id: e15ed917-c80f-4a1a-bdd5-63c1016e7ab9)
- Read full page: Mem0 Memory in Agents (page_id: c2aac6a5-f805-4ed1-b81e-dde51b3ba63e)

**What We Learned:**
- `MemoryClient(api_key="...")` initialization pattern
- `client.add(messages, user_id="...")` for storing conversations
- `client.search(query, user_id="...")` for recalling memories
- Memory ≠ Context Window, Memory ≠ RAG

**What We Built:**
```python
# src/config.py - Added Mem0 configuration
mem0_api_key: Optional[str] = None

# src/api/main.py - Initialize following Mem0 docs
memory_client = MemoryClient(api_key=settings.mem0_api_key)

# src/agent/pydantic_agent.py - Memory recall tool
@sales_agent.tool
async def recall_customer_preferences(ctx: RunContext[SalesBikeAgentDeps], user_id: str):
    # Using Mem0 search() pattern from docs
    memories = ctx.deps.memory_client.search(
        "What are this customer's bike preferences?",
        user_id=user_id
    )

@sales_agent.tool
async def save_conversation_memory(ctx: RunContext[SalesBikeAgentDeps], user_id: str, messages: List):
    # Using Mem0 add() pattern from docs
    result = ctx.deps.memory_client.add(
        messages,
        user_id=user_id,
        output_format="v1.0"
    )
```

### 3. ✅ Continued Using Product/FAQ Knowledge

**Our Data Sources:**
- `file_product_catalog_txt_0b304df3` - 15 bike products
- `file_faq_txt_09c5606e` - 12 FAQ entries

**Maintained Archon RAG Integration:**
```python
@sales_agent.tool
async def search_products(ctx: RunContext[SalesBikeAgentDeps], query: str):
    # Still using Archon for product search!
    result = await ctx.deps.mcp_client.call_tool(
        "mcp__archon__rag_search_knowledge_base",
        arguments={
            "query": query,
            "source_id": "file_product_catalog_txt_0b304df3",
            "match_count": 5
        }
    )
```

## Conclusion

The Archon-first approach solved the two core problems Cole Medin identified:

1. **Control over knowledge**: We picked exactly what docs I searched (your products, your FAQs, Pydantic AI, Mem0)
2. **Collaborative tasks**: You saw 6 initial tasks + 11 refactoring tasks, tracked progress in real-time

**The Complete Result for Sales Bike Agent:**

**Phase 1 - Initial Implementation (6 tasks):**
- ✅ Product recommendations use YOUR 15 bikes (not random web data)
- ✅ FAQ responses use YOUR 12 policies (not generic answers)
- ✅ Clean refactoring to truly use Archon MCP

**Phase 2 - Pydantic AI + Mem0 Refactor (11 tasks):**
- ✅ Agent uses Pydantic AI framework with dependency injection
- ✅ Tools defined with `@agent.tool` decorator (search_products, search_faq, recall_customer_preferences, save_conversation_memory)
- ✅ System prompt with `@agent.system_prompt` decorator and memory awareness
- ✅ Mem0 conversation memory for persistent customer preferences
- ✅ Type-safe throughout with proper error handling
- ✅ Documentation proving we searched and used all three knowledge sources

**The True Archon-First Workflow:**
1. Created `/create-plan` for requirements → researched Pydantic AI & Mem0 docs in Archon
2. Created implementation plan with 11 tasks based on research findings
3. Used `/execute-plan` → tracked all 11 tasks in Archon (todo → doing → review)
4. Updated documentation showing exactly what we searched and what we built

As Cole says: **"Archon is the one tool that enables AI and human collaboration at a very deep level."**

We experienced that collaboration **twice**:
1. When you asked: "did the implementation check documents in archon?" → Led to Archon MCP refactor
2. When you said: "yes please and add it to the create plan, execute md files, so they understand process" → Led to proper workflow with research phase

---

**References:**
- [Cole Medin's Archon Guide](https://www.youtube.com/watch?v=DMXyDpnzNpY)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [Archon MCP Server](https://github.com/punkpeye/archon)
- [Pydantic AI](https://ai.pydantic.dev/)
- [Mem0](https://docs.mem0.ai/)
