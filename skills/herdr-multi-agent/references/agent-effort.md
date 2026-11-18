# Agent and effort map

Single source of truth for coordinator and worker model tiers and selectable presets. Pair the chosen preset row with your host protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), or [protocols/fallback.md](protocols/fallback.md)) in [topology.md](topology.md) when starting agents.

## Default (Preset 3: Coordinator = Middle, Worker = Top)

| Role | Family (`--kind`) | Agent | Effort | Protocol |
|------|-------------------|-------|--------|----------|
| Coordinator | `claude` | Claude Opus 5.5 (`claude-opus-5-5`) | medium | [protocols/claude.md](protocols/claude.md) |
| Coordinator | `agy` | Gemini 4 Argon (`gemini-4-argon-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Worker | `claude` | Claude Fable 5.2 (`claude-fable-5-2`) | medium | [protocols/claude.md](protocols/claude.md) |
| Worker | `agy` | Gemini 4 Carbon (`gemini-4-carbon-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Coordinator / Worker | other `--kind` | Host default (bare start) | host default | [protocols/fallback.md](protocols/fallback.md) |

## Tier hierarchy and selectable presets

Model tiers from highest to lowest (all run at `medium` effort by default):

- **Top:** `Claude Fable 5.2` (`claude-fable-5-2`) / `Gemini 4 Carbon` (`gemini-4-carbon-medium`)
- **Middle:** `Claude Opus 5.5` (`claude-opus-5-5`) / `Gemini 4 Argon` (`gemini-4-argon-medium`)
- **Fast:** `Claude Sonnet 4.6` (`claude-sonnet-4-6`) / `Gemini 4 Hydrogen` (`gemini-4-hydrogen-medium`)

The person can pick any preset below; **Preset 3** is the default:

| Preset | Coordinator -> Worker | `claude` (Coordinator / Worker) | `agy` (Coordinator / Worker) |
|--------|-----------------------|---------------------------------|------------------------------|
| 1 | Top -> Middle | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-carbon-medium` / `gemini-4-argon-medium` |
| 2 | Middle -> Fast | `claude-opus-5-5` / `claude-sonnet-4-6` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` |
| **3 (default)** | Middle -> Top | `claude-opus-5-5` / `claude-fable-5-2` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-carbon-medium` |
| 4 (asymmetric) | `claude`: Top -> Middle; `agy`: Middle -> Fast | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` |

- Coordinator and worker are different roles: by default (Preset 3), the coordinator plans waves, overlap and merges on the middle tier (`Opus 5.5` or `Argon`), and each worker implements one task on the top tier (`Fable 5.2` or `Carbon`). Every preset runs at `medium` effort.
- A worker is always of the same family as its coordinator: take the worker row whose `--kind` matches the coordinator's ([topology.md](topology.md)).
- Host-specific `--` flag syntax (`--model` + `--effort` on `claude`, `--model` alone on `agy`, bare start on other kinds) and two-tier `code-review` reviewer model mapping (`flagship` vs `fast/balanced`) live in the protocol files ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/fallback.md](protocols/fallback.md)).
- Review sub-agents or fallback review panes dispatched by a worker stay in the worker's agent family unless the person explicitly overrides it.
- The person can override the preset (1–4) or any individual row; say so in the first prompt so the worker does not assume the default.
