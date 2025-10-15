---
name: "Create Implementation Plan from Requirements"
description: Create a comprehensive implementation plan from requirements document through extensive research and analysis
argument-hint: [requirements-file-path]
---

# Create Implementation Plan from Requirements

You are about to create a comprehensive implementation plan based on initial requirements. This involves extensive research, analysis, and planning to produce a detailed roadmap for execution.

## Step 1: Read and Analyze Requirements

Read the requirements document from: $ARGUMENTS

Extract and understand:
- Core feature requests and objectives
- Technical requirements and constraints
- Expected outcomes and success criteria
- Integration points with existing systems
- Performance and scalability requirements
- Any specific technologies or frameworks mentioned

## Step 2: Research Phase

### 2.1 Knowledge Base Search (if Archon available)
If Archon RAG is available and relevant:
- List sources: `rag_get_available_sources()`
- Search for relevant patterns: `rag_search_knowledge_base(query="...")`
- Find code examples: `rag_search_code_examples(query="...")`
- Focus on implementation patterns, best practices, and similar features

Recommended query seeds for Sales Bike:
- "agent architecture", "memory patterns", "vector search ranking"
- "catalog schema", "faq ingestion", "lead capture"

### 2.2 Codebase Analysis (for existing projects)
If this is for an existing codebase:
- Identify service layer, module structure, naming, and testing setup
- Note error handling, configuration patterns, and DTO/request shapes
- Extract conventions to follow in the plan

If no existing code is present, skip pattern extraction and rely entirely on Archon Knowledge.

## Step 3: Produce Implementation Plan (PRP)
Create `PRPs/sales_bike_agent.md` with:
- Task breakdown with dependencies and rough effort
- Technical architecture and integration points (API, RAG, vector store)
- Data flows for product catalog and FAQ usage
- Testing strategy (unit + integration) and success criteria
- Risks and open questions

## Output
- Save the plan to `PRPs/sales_bike_agent.md`
- Provide a short executive summary and next steps

## Usage
/create-plan sales_bike/Data/goal.md

