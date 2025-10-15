---
name: "primer"
description: "Loads project context and sets up Archon-first workflow environment"
---

# primer

You are working in the Sales Bike repository. Load the following context:
- Global rules in .claude/CLAUDE.md
- Project name: "Sales Bike Agent" (use for Archon MCP projects/tasks)
- Knowledge sources in Archon: Pydantic AI docs, Mem0 docs, Sales Bike data (faq.txt, product_catalog.txt, product_catalog.md if present)
- Code patterns from this repo (services, testing, naming)

Behavior:
- Prefer Archon RAG for facts; cite chunks when helpful
- Manage tasks in Archon project
- Do not assume catalog data; retrieve via Archon MCP
- If no existing code is present, skip pattern extraction and rely entirely on Archon Knowledge

