# Agent and effort map

Which agent and effort level to start for each kind of task. Use it in [topology.md](topology.md) when creating agents.

| Role | Agent | Effort |
|------|-------|--------|
| Coordinator | Claude Opus 5.5 | high |
| Coordinator | Argon | high |
| Worker | Claude Sonnet 5.5 | medium |
| Worker | Flash 3.8 | medium |

- Coordinator and worker are different roles with different budgets: planning waves, overlap and merges gets the high effort, implementing one task gets medium.
- Sub-agents dispatched by a worker for review follow the worker's agent family and effort unless the person says otherwise.
- The person can override any row; say so in the first prompt so the worker does not assume the default.
