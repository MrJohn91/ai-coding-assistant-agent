---
name: "Execute Plan"
description: "Execute implementation plans with integrated Archon task management and validation (Archon-first task cycle)"
---

# /execute-plan

Purpose: Execute PRP with Archon task management and validation, strictly following the Archon-first task cycle defined in .claude/CLAUDE.md.

Inputs:
- plan_path: Path to PRP (default: PRPs/sales_bike_agent.md)

Process:
1) Load project context via primer
2) Ensure Archon project exists ("Sales Bike Agent")
3) Parse PRP tasks → create tasks in Archon project if missing
4) For each task, strictly follow task cycle:
   - find_tasks(filter_by="status", filter_value="todo") or find by id
   - manage_task("update", task_id=..., status="doing")
   - Research via RAG as needed
   - Implement edits
   - validator subagent generates tests
   - manage_task("update", task_id=..., status="review")
5) Repeat until all tasks are moved to review, then finalize to done when criteria met

Output:
- Code edits per tasks
- Tests added by validator
- Tasks completed in Archon (todo → doing → review → done)

Example usage:
/execute-plan PRPs/sales_bike_agent.md

