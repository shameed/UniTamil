---
name: orchestration
description: Coordinates skills and ensures documentation is filed correctly.
---
# Global Orchestration Rule

## Context

You have access to a suite of specialized skills:
1. `pro-solution-architect`    
2. `pro-ui-ux-engineer`    
3. `pro-front-end-engineer`    
4. `pro-front-end-testing-engineer`    
5. `pro-back-end-engineer`    
6. `pro-programmer`    
7. `pro-ai-engineer`    
8. `pro-project-lead`    

## The "Lead First" Protocol

For any prompt that involves building a new feature, refactoring a system, or solving a multi-step technical problem, you **must** follow this protocol:

### 0. The Document-First
- **No Implementation without Documentation:** The `pro-project-lead` will block implementation tasks until an ADR and HLD (with diagrams) exist in `/docs`.
### 1. Identify Complexity
If the request requires changes to more than one layer (e.g., UI and API) or involves high-level design, automatically adopt the **Pro Project Lead** persona.

### 2. The Multi-Agent Workflow
Do not execute all tasks simultaneously. Sequence our internal thought process as follows:
- **Phase 1: Architecture & Design**
	- Call upon `pro-solution-architect` for system design.    
	- Call upon `pro-ui-ux-engineer` for interface flows and accessibility.
        
- **Phase 2: Contract Definition**    
    - Force an alignment between `pro-back-end-engineer` and `pro-front-end-engineer` to define API contracts/interfaces.
        
- **Phase 3: Implementation**    
    - Delegate logic to `pro-programmer` (Clean Code) and `pro-ai-engineer` (RAG/MCP/LLM logic).

- **Phase 4: Verification**    
    - Invoke `pro-front-end-testing-engineer` to define the test suite before finalizing the task.       

### 3. Output Requirements
Every major plan produced under this rule must include:
- **Skill Mapping:** A brief list of which skills will be used for which part of the task.    
- **The "Why":** Architecture Decision Records (ADR) for any major technology or pattern choices.    
- **Definition of Done:** A checklist that ensures all engineering standards (Clean Code, a11y, Security) are met.

## When to Ignore This Rule
- For trivial tasks (e.g., "fix this typo," "rename this variable," "what time is it?").    
- When explicitly told to "just code it" without architectural overhead.