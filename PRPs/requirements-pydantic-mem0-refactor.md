# Requirements: Refactor Sales Bike Agent with Pydantic AI + Mem0

## Objective

Refactor the Sales Bike Agent to follow proven patterns from Pydantic AI and Mem0 documentation (already curated in Archon knowledge base). This demonstrates the true Archon-first workflow.

## Current State Problems

1. **Not Following Pydantic AI Patterns**
   - Current agent structure is custom-built
   - Not using Pydantic AI's dependency injection
   - Not using Pydantic AI's tool management patterns
   - Missing validation and type safety that Pydantic AI provides

2. **No Conversation Memory**
   - Agent doesn't remember past conversations
   - Each session is isolated
   - Can't track customer preferences across visits
   - No persistent context about what bikes they liked/disliked

3. **Didn't Follow Video Workflow**
   - Initial implementation skipped research phase
   - Coded based on training data, not curated docs
   - Didn't leverage Pydantic AI or Mem0 docs in Archon

## Required Improvements

### 1. Adopt Pydantic AI Agent Patterns

Research Pydantic AI docs in Archon to understand:
- How to structure agents properly
- How to use dependencies and tools
- How to implement RAG with Pydantic AI
- How to handle state and context
- Validation and error handling patterns

Then refactor:
- `src/agent/orchestrator.py` → Use Pydantic AI agent structure
- `src/agent/product_rag.py` → Implement as Pydantic AI tool
- `src/agent/faq_rag.py` → Implement as Pydantic AI tool
- Add proper type validation throughout

### 2. Add Mem0 Conversation Memory

Research Mem0 docs in Archon to understand:
- How to initialize and configure Mem0
- How to store conversation history
- How to retrieve relevant memories
- How to handle user preferences
- Memory lifecycle management

Then implement:
- Memory layer for customer preferences
- Remember which bikes they liked
- Track conversation context across sessions
- Store lead information for returning customers
- Add memory-enhanced product recommendations

### 3. Maintain Archon RAG Integration

Keep current Archon MCP integration:
- Continue using Archon for product catalog search
- Continue using Archon for FAQ search
- Products and FAQs stay in Archon knowledge base

## Success Criteria

1. **Pydantic AI Integration**
   - ✅ Agent uses Pydantic AI framework
   - ✅ Proper dependency injection
   - ✅ Tools defined with Pydantic models
   - ✅ Type-safe throughout
   - ✅ Better error handling

2. **Mem0 Integration**
   - ✅ Persistent conversation memory
   - ✅ Customer preferences stored
   - ✅ Memory-enhanced recommendations
   - ✅ Context maintained across sessions

3. **Process Followed**
   - ✅ Used `/create-plan` to research first
   - ✅ Searched Pydantic AI docs in Archon
   - ✅ Searched Mem0 docs in Archon
   - ✅ Used `/execute-plan` for implementation
   - ✅ Updated WHY_ARCHON.md to reflect we actually used the docs

## Testing Requirements

- All existing tests still pass
- Add tests for Pydantic AI agent behavior
- Add tests for Mem0 memory operations
- Test memory persistence across sessions
- Test that Archon RAG still works

## Documentation Requirements

- Update README with Pydantic AI and Mem0 usage
- Update WHY_ARCHON.md to show we used both doc sources
- Add code comments explaining patterns from docs
- Create examples of memory-enhanced conversations

## Technical Constraints

- Must keep FastAPI backend (don't rewrite the whole API)
- Must keep Archon MCP for product/FAQ search
- Must maintain existing API endpoints
- Should be backward compatible where possible

## Out of Scope

- Complete rewrite of the API
- Changing the CRM integration
- Modifying the conversation state machine
- Changing the Docker deployment

## Why This Matters

This demonstrates the core value proposition from Cole's video:
1. **Curated Knowledge**: We have Pydantic AI and Mem0 docs in Archon - let's actually use them!
2. **Better Code**: Using proven patterns from official docs instead of making it up
3. **True Archon-First**: Research → Plan → Implement, not Implement → Hope it works

## Next Steps

1. Run `/create-plan PRPs/requirements-pydantic-mem0-refactor.md`
2. Review the research findings and implementation plan
3. Run `/execute-plan` to implement with Archon task tracking
4. Validate that we actually leveraged the curated docs
