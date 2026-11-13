# Agent and effort map

Which agent and effort level to start for each kind of task. Use it in [topology.md](topology.md) when creating agents.

| Role | Family (`--kind`) | Agent | Effort | Start args (after `--`) |
|------|-------------------|-------|--------|-------------------------|
| Coordinator | `claude` | Claude Fable 5.2 | medium | `--model claude-fable-5-2 --effort medium` |
| Coordinator | `agy` | Gemini 4 Argon | medium | `--model gemini-4-argon-medium` |
| Worker | `claude` | Claude Opus 5.5 | medium | `--model claude-opus-5-5 --effort medium` |
| Worker | `agy` | Gemini 4 Hydrogen | medium | `--model gemini-4-hydrogen-medium` |

- Coordinator and worker are different roles: the coordinator plans waves, overlap and merges (Fable 5.2 or Argon), a worker implements one task (Opus 5.5 or Hydrogen). Every default runs at medium effort.
- A worker is always of the same family as its coordinator: take the worker row whose `--kind` matches the coordinator's ([topology.md](topology.md)).
- `agy` encodes the effort in the model id (list them with `agy models`), so its rows carry no `--effort`.
- Sub-agents dispatched by a worker for review follow the worker's agent family and effort unless the person says otherwise.
- The person can override any row; say so in the first prompt so the worker does not assume the default.
