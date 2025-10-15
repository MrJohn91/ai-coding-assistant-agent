# AI Coding Workflow Guide

This guide documents the complete workflow used to build the Sales Bike Agent, based on AI development methodology. Follow this process for any future AI agent projects.

---

## 📊 Workflow Diagram

```
╔═════════════════════════════════════════════════════════════════════════════╗
║                         DEVELOP AI CODING WORKFLOWS          ║
║                                                                              ║
║  Primary Mental Model for AI Coding:                                        ║
║  ┌────────────────────────────────────────────────────────────────────┐    ║
║  │  1. Planning  ───▶  2. Implementation  ───▶  3. Validation         │    ║
║  └────────────────────────────────────────────────────────────────────┘    ║
╚═════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                        STEPS TO PLANNING                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. "Vibe plan"                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Explore ideas, architecture, concepts, tech stack, etc.             │  │
│  │  with the AI coding assistant. NOT structured.                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────┐                       │
│  │  New projects → research from online resources, │                       │
│  │                 previous projects, etc.         │                       │
│  │                                                  │                       │
│  │  Existing projects → research/analyze the       │                       │
│  │                      existing codebase          │                       │
│  └─────────────────────────────────────────────────┘                       │
│                                    ↓                                         │
│  2. Create the INITIAL.md with the AI coding assistant                     │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  The goal is to produce a markdown document with a                   │  │
│  │  detailed feature request (a PRD).                                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌─────────────────────────────────────────────────┐                       │
│  │  New projects → High level, simple MVP,         │                       │
│  │                 include references to           │                       │
│  │                 supporting docs/examples        │                       │
│  │                                                  │                       │
│  │  Existing projects → Focused and detailed,      │                       │
│  │                      include references to      │                       │
│  │                      "integration points"       │                       │
│  └─────────────────────────────────────────────────┘                       │
│                                    ↓                                         │
│  3. Prepare each core "component of context engineering" (slash commands   │
│     make this easy!)                                                        │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                     CONTEXT ENGINEERING                            │    │
│  │                                                                     │    │
│  │           ┌─────────────────────────────────┐                      │    │
│  │           │                                 │                      │    │
│  │           │            ┌────────┐           │                      │    │
│  │           │            │  RAG   │           │                      │    │
│  │           │            └────────┘           │                      │    │
│  │           │        ┌───────┴──────┐         │                      │    │
│  │           │        │              │         │                      │    │
│  │      ┌────┴────┐   │    ┌─────────┴──────┐ │                      │    │
│  │      │ Memory  │───┼────│ Task           │ │                      │    │
│  │      │         │   │    │ Management     │ │                      │    │
│  │      └─────────┘   │    └────────────────┘ │                      │    │
│  │                    │                        │                      │    │
│  │              ┌─────┴────────┐               │                      │    │
│  │              │   Prompt     │               │                      │    │
│  │              │ Engineering  │               │                      │    │
│  │              └──────────────┘               │                      │    │
│  │                                             │                      │    │
│  │    The goal is to prepare/combine each component for the AI to    │    │
│  │    have goals/tasks/resources based on your PRD.                  │    │
│  │                                                                     │    │
│  │    Basically taking your PRD and figuring out what context you    │    │
│  │    need to give the agent (that is exactly what /primer does)     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  Tools for Context Engineering:                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  • Archon     → Project/task/RAG management                        │    │
│  │  • PRD        → Product requirements document                      │    │
│  │  • Web Search → Research frameworks, patterns, examples            │    │
│  │  • etc...     → Any tool that helps gather/organize context        │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                  STEPS TO IMPLEMENTING/VALIDATING                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Execute the implementation plan task by task                            │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Most of the structure has been set up during planning.              │  │
│  │  Now we execute "slash commands" for coding/workflow.                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  2. Validate the produced code                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  At this point the AI coding assistant has the context               │  │
│  │  it needs - most of the structure is already in place!               │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    TRUST BUT VERIFY                                │    │
│  │                                                                     │    │
│  │  You can let the AI coding assistant run wild at this point,      │    │
│  │  but typically you want to monitor it to ensure it is             │    │
│  │  following the plan.                                               │    │
│  │                                                                     │    │
│  │  ┌─────────────────────┐      ┌──────────────────────┐           │    │
│  │  │ Human Validation    │      │ AI Coding Assistant  │           │    │
│  │  │                     │      │    Validation        │           │    │
│  │  ├─────────────────────┤      ├──────────────────────┤           │    │
│  │  │ • Performs          │      │ • Unit Tests         │           │    │
│  │  │   manual tests      │      │ • Runs               │           │    │
│  │  │                     │      │                      │           │    │
│  │  │ • Runs              │      │ • Integration Tests  │           │    │
│  │  │   integration tests │      │ • Runs               │           │    │
│  │  └─────────────────────┘      └──────────────────────┘           │    │
│  │                                                                     │    │
│  │  Use your MCP servers correctly:                                  │    │
│  │  - Is reading/editing the right files                             │    │
│  │  - Leverage your tasks properly (Archon, Claude Task Master,      │    │
│  │    TASKS.md, etc.)                                                 │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                    TASK CYCLE                                   │       │
│  │                                                                  │       │
│  │  ┌─────────┐                                                    │       │
│  │  │  Todo   │──────┐                                             │       │
│  │  └─────────┘      │                                             │       │
│  │       ↑           ↓                                             │       │
│  │       │      ┌─────────┐                                        │       │
│  │  ┌─────────┐ │ Doing   │                                        │       │
│  │  │  Done   │←└─────────┘                                        │       │
│  │  └─────────┘      ↓                                             │       │
│  │       ↑      ┌─────────┐                                        │       │
│  │       └──────│ Review  │                                        │       │
│  │              └─────────┘                                        │       │
│  │                                                                  │       │
│  │  For each task:                                                 │       │
│  │  1. find_tasks(status="todo") → Get next task                  │       │
│  │  2. manage_task(status="doing") → Mark as in progress          │       │
│  │  3. Research with RAG if needed                                │       │
│  │  4. Implement the code                                          │       │
│  │  5. manage_task(status="review") → Mark for validation         │       │
│  │  6. Test and verify                                             │       │
│  │  7. manage_task(status="done") → Complete                      │       │
│  │  8. Repeat until all tasks done                                │       │
│  └─────────────────────────────────────────────────────────────────┘       │
│                                                                              │
│  AI Coding Concepts at Each Step:                                           │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Planning           Implementation      Validation                 │    │
│  │  ─────────────      ──────────────      ──────────────            │    │
│  │  includes:          includes:           includes:                  │    │
│  │  • Status Rules     • Status Rules      • Status Rules            │    │
│  │  • Blueprints       • Blueprints        • Blueprints              │    │
│  │                     • Slash Commands    • Slash Commands          │    │
│  │                                                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Detailed Step-by-Step Process

### PHASE 1: PLANNING (Before Writing Code)

#### Step 1.1: Define Requirements
Create a requirements document answering:

**Questions to Answer:**
- What problem does this agent solve?
- What actions must the agent perform?
- What data sources does it need?
- What APIs/services will it integrate with?
- Who will use it and how?
- What defines success?

**Example (Sales Bike Agent):**
```
Problem: Online bike shop needs 24/7 sales assistance
Actions:
  - Recommend products based on needs
  - Answer FAQ questions
  - Capture leads when customers show interest
Data Sources: Product catalog, FAQ database
APIs: OpenAI (LLM), Mem0 (memory), CRM system
Users: Bike shop customers
Success: Qualified leads captured, customer questions answered
```

#### Step 1.2: Research with Archon RAG

**Before coding, research:**

```python
# 1. Get available documentation sources
rag_get_available_sources()

# 2. Search framework docs
rag_search_knowledge_base(
    query="Pydantic AI agent tools",
    source_id="pydantic_docs_id",
    match_count=5
)

# 3. Find code examples
rag_search_code_examples(
    query="dependency injection",
    source_id="pydantic_docs_id",
    match_count=3
)

# 4. Research integrations
rag_search_knowledge_base(
    query="Mem0 conversation memory",
    source_id="mem0_docs_id"
)
```

**Create research notes:**
- Document key patterns found
- Save code examples
- Note important configuration details
- Identify potential challenges

#### Step 1.3: Create Project in Archon

```python
# Create project
project = manage_project(
    action="create",
    title="Sales Bike Agent",
    description="AI sales assistant for bike shop with lead capture",
    github_repo="https://github.com/username/sales-bike"
)

project_id = project["project"]["id"]
```

#### Step 1.4: Break Down Into Tasks

**Task Granularity Rules:**
- Each task = 30 min to 4 hours of work
- Make tasks specific and measurable
- Include clear completion criteria
- Order by dependency (what must happen first)

**Example Task Breakdown:**

```python
# Setup tasks
manage_task("create",
    project_id=project_id,
    title="Setup project structure",
    description="Create directories, requirements.txt, .env.example",
    task_order=100,
    assignee="User"
)

manage_task("create",
    project_id=project_id,
    title="Research Pydantic AI patterns",
    description="Study agent creation, tools, dependencies from docs",
    task_order=95,
    assignee="User"
)

# Implementation tasks
manage_task("create",
    project_id=project_id,
    title="Create Pydantic AI agent structure",
    description="Define agent, deps_type, system prompt",
    task_order=90
)

manage_task("create",
    project_id=project_id,
    title="Implement search_products tool",
    description="Tool to search product catalog with FAISS/Archon RAG",
    task_order=85
)

manage_task("create",
    project_id=project_id,
    title="Implement search_faq tool",
    description="Tool to answer customer questions from FAQ",
    task_order=80
)

manage_task("create",
    project_id=project_id,
    title="Integrate Mem0 memory",
    description="Add recall_customer_preferences and save_conversation tools",
    task_order=75
)

manage_task("create",
    project_id=project_id,
    title="Implement lead capture",
    description="capture_lead tool with email validation and CRM integration",
    task_order=70
)

# Testing tasks
manage_task("create",
    project_id=project_id,
    title="Create Postman test collection",
    description="Test all endpoints with complete customer journey",
    task_order=50
)

manage_task("create",
    project_id=project_id,
    title="Write unit tests",
    description="Test individual tools and functions",
    task_order=45
)

# Documentation tasks
manage_task("create",
    project_id=project_id,
    title="Write README",
    description="Setup instructions, API docs, architecture overview",
    task_order=30
)
```

---

### PHASE 2: IMPLEMENTATION (Task-Driven Development)

#### The Task Cycle (Repeat for Each Task)

**1. Get Next Task**
```python
# Find highest priority todo task
tasks = find_tasks(
    filter_by="status",
    filter_value="todo",
    project_id=project_id
)

# Pick task with highest task_order
current_task = tasks[0]
```

**2. Mark Task as Doing**
```python
manage_task(
    action="update",
    task_id=current_task["id"],
    status="doing"
)
```

**3. Research (If Needed)**
```python
# Search for relevant documentation
rag_search_knowledge_base(
    query="Pydantic AI tool decorator",
    match_count=3
)

# Find code examples
rag_search_code_examples(
    query="agent tool async",
    match_count=2
)

# Read full documentation pages if needed
rag_read_full_page(
    page_id="specific_page_uuid"
)
```

**4. Implement**
- Write code based on research
- Follow patterns from documentation
- Test locally as you code
- Keep it simple and focused on task goal

**5. Mark for Review**
```python
manage_task(
    action="update",
    task_id=current_task["id"],
    status="review"
)
```

**6. Validate & Complete**
- Test the implementation
- Verify it meets task description
- If good, mark done:
```python
manage_task(
    action="update",
    task_id=current_task["id"],
    status="done"
)
```

**7. Repeat**
- Get next todo task
- Continue cycle until all tasks complete

#### Code Organization Best Practices

**Directory Structure:**
```
project/
├── src/
│   ├── agent/              # AI agent logic
│   │   ├── pydantic_agent.py    # Main agent + tools
│   │   ├── dependencies.py      # Dependency injection
│   │   └── prompts.py           # System prompts
│   ├── api/                # FastAPI application
│   │   ├── main.py              # Server + endpoints
│   │   └── models.py            # Request/response models
│   ├── mcp/                # MCP bridge (if using Archon)
│   ├── vector_store/       # Vector search (FAISS, etc)
│   ├── llm/                # LLM abstraction layer
│   └── data/               # Data processing
├── data/                   # Data files
├── tests/                  # Tests
├── docs/                   # Documentation
├── .env.example            # Environment template
├── requirements.txt        # Dependencies
└── README.md              # Main documentation
```

**Key Files to Create:**

1. **Agent Definition** (`src/agent/pydantic_agent.py`)
```python
from pydantic_ai import Agent, RunContext

# Define agent with dependencies
agent = Agent(
    'openai:gpt-4o',
    deps_type=YourDepsClass,
    retries=2
)

@agent.tool
async def your_tool(ctx: RunContext[YourDeps], arg: str):
    """Tool docstring - explain what it does."""
    # Access dependencies: ctx.deps.some_service
    return result

@agent.system_prompt
async def get_system_prompt(ctx: RunContext[YourDeps]) -> str:
    """Return system prompt string."""
    return "You are a helpful assistant..."
```

2. **Dependencies** (`src/agent/dependencies.py`)
```python
from dataclasses import dataclass

@dataclass
class YourAgentDeps:
    """Dependencies for your agent."""
    # External services
    api_client: Any
    memory_client: Any
    # Data sources
    vector_store: Any
    # Configuration
    config: Any
```

3. **FastAPI Server** (`src/api/main.py`)
```python
from fastapi import FastAPI

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load resources
    yield
    # Shutdown: Cleanup

@app.post("/api/messages")
async def send_message(message: str):
    deps = YourDeps(...)
    result = await agent.run(message, deps=deps)
    return {"response": result.data}
```

---

### PHASE 3: VALIDATION (Testing & Documentation)

#### Testing Strategy

**1. Unit Tests** (test individual functions)
```python
# tests/unit/test_tools.py
import pytest

@pytest.mark.asyncio
async def test_search_products():
    # Test tool function directly
    ctx = create_mock_context()
    result = await search_products(ctx, "mountain bike")
    assert len(result) > 0
```

**2. Integration Tests** (test components together)
```python
# tests/integration/test_agent.py
@pytest.mark.asyncio
async def test_agent_product_search():
    deps = create_test_deps()
    result = await agent.run("I need a bike", deps=deps)
    assert "bike" in result.data.lower()
```

**3. API Tests** (test HTTP endpoints)
- Create Postman collection
- Test complete user journeys
- Verify response formats
- Test error handling

**4. Manual Testing**
- Test edge cases
- Verify user experience
- Check conversation flow
- Test with real data

#### Documentation Checklist

**README.md must include:**
- [ ] Project description
- [ ] Features list
- [ ] Tech stack
- [ ] Quick start instructions
- [ ] API endpoints table
- [ ] Configuration options
- [ ] Testing instructions
- [ ] Troubleshooting section
- [ ] Architecture diagram
- [ ] Example usage

**Additional Docs:**
- API design document
- Architecture decisions
- Deployment guide
- Contributing guidelines

---

## 🛠️ Tools & Technologies

### Core Tools

**1. Archon MCP** - Project & Knowledge Management
```python
# Project management
manage_project(), find_projects()

# Task management
manage_task(), find_tasks()

# Knowledge base
rag_search_knowledge_base()
rag_search_code_examples()
rag_read_full_page()
```

**2. Pydantic AI** - Agent Framework
```python
# Agent creation
Agent(model, deps_type, retries)

# Tool definition
@agent.tool
async def tool_name(ctx, args): ...

# System prompt
@agent.system_prompt
async def get_prompt(ctx): ...

# Running agent
await agent.run(prompt, deps=deps)
```

**3. Mem0** - Conversation Memory
```python
# Initialize
client = MemoryClient(api_key="...")

# Store memory
client.add(messages, user_id="...")

# Recall memory
client.search(query, user_id="...")
```

**4. FastAPI** - Web Framework
```python
# Create app
app = FastAPI(lifespan=lifespan)

# Define endpoints
@app.post("/api/messages")
async def endpoint(): ...
```

### Development Tools

- **Git**: Version control with clear commits
- **Postman**: API testing
- **Pytest**: Unit and integration testing
- **Docker**: Containerization (optional)
- **Claude Code**: AI-assisted development

---

## 📋 Project Checklist

### Planning Phase
- [ ] Requirements document created
- [ ] Archon MCP sources loaded (documentation)
- [ ] Research completed (framework, APIs, patterns)
- [ ] Project created in Archon
- [ ] Tasks broken down and prioritized
- [ ] Architecture designed

### Implementation Phase
- [ ] Project structure created
- [ ] Dependencies installed
- [ ] Environment configured
- [ ] Agent and tools implemented
- [ ] API endpoints created
- [ ] Data sources integrated
- [ ] Error handling added
- [ ] Logging configured
- [ ] All tasks marked complete in Archon

### Validation Phase
- [ ] Unit tests written and passing
- [ ] Integration tests passing
- [ ] Postman collection created
- [ ] Manual testing completed
- [ ] README written
- [ ] API documentation complete
- [ ] Architecture documented
- [ ] Code reviewed

### Deployment (if applicable)
- [ ] Environment variables documented
- [ ] Docker configuration (if used)
- [ ] Deployment instructions
- [ ] Monitoring setup
- [ ] Error tracking

---

## 🎓 Key Principles

### 1. Research First, Code Second
Never start coding without researching:
- Framework documentation
- Integration guides
- Code examples
- Best practices

### 2. Task-Driven Development
- Always work from Archon tasks
- One task at a time
- Update task status regularly
- Only ONE task in "doing" status

### 3. Dependency Injection
- Use Pydantic AI deps_type pattern
- All external services in dependencies
- Easy to test and mock
- Clear separation of concerns

### 4. Tool-Based Agent Design
- Each capability = one tool
- Tools are async functions
- Tools have clear docstrings
- Tools return structured data

### 5. Iterative Development
- Start simple, add complexity gradually
- Test each component before moving on
- Refactor when patterns emerge
- Keep code clean and documented

### 6. Documentation-Driven
- Document as you build
- Clear README
- Code comments for complex logic
- API documentation

---

## 🚀 Quick Start Template

Use this template for your next project:

```bash
# 1. Create project structure
mkdir my_agent && cd my_agent
mkdir -p src/{agent,api,mcp,data} tests docs data

# 2. Setup Archon
# - Create project in Archon
# - Create initial tasks
# - Load documentation to Archon knowledge base

# 3. Research
# - Search Archon for framework docs
# - Find code examples
# - Document patterns

# 4. Create files
touch src/agent/pydantic_agent.py
touch src/agent/dependencies.py
touch src/api/main.py
touch requirements.txt
touch .env.example
touch README.md

# 5. Follow task cycle
# - Get task → Mark doing → Research → Implement → Review → Done

# 6. Test
pytest tests/
# Create Postman collection

# 7. Document
# Update README with setup and usage
```

---

## 📚 Example: Sales Bike Agent

This project followed this exact workflow:

### Planning
- **Requirements**: Sales assistant for bike shop
- **Research**: Pydantic AI, Mem0, FastAPI docs loaded to Archon
- **Tasks**: 15 tasks created, prioritized by dependency

### Implementation
- **Task 1**: Setup project structure ✓
- **Task 2**: Research Pydantic AI ✓
- **Task 3**: Create agent skeleton ✓
- **Task 4**: Implement search_products tool ✓
- **Task 5**: Implement search_faq tool ✓
- **Task 6**: Integrate Mem0 ✓
- **Task 7**: Add lead capture ✓
- **Task 8**: Create FastAPI endpoints ✓

### Validation
- **Testing**: Postman collection with 13 tests ✓
- **Documentation**: README, TESTING_GUIDE, API docs ✓
- **Result**: Fully functional agent with lead capture ✓

---

## 🔄 Continuous Improvement

After completing a project:

1. **Retrospective**
   - What worked well?
   - What could be improved?
   - What patterns emerged?

2. **Update Templates**
   - Add new patterns to this guide
   - Update code templates
   - Document lessons learned

3. **Share Knowledge**
   - Add successful patterns to Archon
   - Create reusable components
   - Document for future projects

---

## 📞 Support

For questions about this workflow:
1. Review this guide
2. Check example project (Sales Bike Agent)
3. Search Archon knowledge base
4. Consult framework documentation

---

**Remember**: The key to success is following the cycle:
**Plan → Research → Implement → Validate → Repeat**

Use Archon as your central hub for project management, knowledge, and task tracking.

Happy coding! 🚀
