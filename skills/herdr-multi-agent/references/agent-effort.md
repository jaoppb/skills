# Agent and effort map

Single source of truth for coordinator and worker model tiers and selectable presets. Pair the chosen preset row with your host protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), or [protocols/fallback.md](protocols/fallback.md)) in [topology.md](topology.md) when starting agents.

## Default (Preset 3: Coordinator = Middle, Worker = Top)

| Role | Family (`--kind`) | Agent | Effort | Protocol |
|------|-------------------|-------|--------|----------|
| Coordinator | `claude` | Claude Opus 5.5 (`claude-opus-5-5`) | medium | [protocols/claude.md](protocols/claude.md) |
| Coordinator | `agy` | Gemini 4 Argon (`gemini-4-argon-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Coordinator | `kiro` | Claude Sonnet (`<sonnet-id>` via `kiro-cli`) | medium | [protocols/kiro.md](protocols/kiro.md) |
| Worker | `claude` | Claude Fable 5.2 (`claude-fable-5-2`) | medium | [protocols/claude.md](protocols/claude.md) |
| Worker | `agy` | Gemini 4 Carbon (`gemini-4-carbon-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Worker | `kiro` | Claude Opus (`<opus-id>` via `kiro-cli`) | medium | [protocols/kiro.md](protocols/kiro.md) |
| Coordinator / Worker | other `--kind` | Host default (bare start) | host default | [protocols/fallback.md](protocols/fallback.md) |

## Tier hierarchy and selectable presets

Model tiers from highest to lowest (all coordinator and worker presets run at `medium` effort by default; `<opus-id>` and `<sonnet-id>` on `kiro` are the newest `claude-opus-*` and `claude-sonnet-*` slugs resolved from `kiro-cli chat --list-models --format json` via `sync_kiro_agents.py --print-models`):

- **Top:** `Claude Fable 5.2` (`claude-fable-5-2`) / `Gemini 4 Carbon` (`gemini-4-carbon-medium`) / Kiro `claude-opus-*` (`<opus-id>`)
- **Middle:** `Claude Opus 5.5` (`claude-opus-5-5`) / `Gemini 4 Argon` (`gemini-4-argon-medium`) / Kiro `claude-sonnet-*` (`<sonnet-id>`)
- **Fast:** `Claude Sonnet 4.6` (`claude-sonnet-4-6`) / `Gemini 4 Hydrogen` (`gemini-4-hydrogen-medium`) / Kiro `claude-sonnet-*` (`<sonnet-id>`, never Haiku for workers)

The person can pick any preset below; **Preset 3** is the default:

| Preset | Coordinator -> Worker | `claude` (Coordinator / Worker) | `agy` (Coordinator / Worker) | `kiro` (Coordinator / Worker) |
|--------|-----------------------|---------------------------------|------------------------------|-------------------------------|
| 1 | Top -> Middle | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-carbon-medium` / `gemini-4-argon-medium` | `<opus-id>` / `<sonnet-id>` (`--effort medium`) |
| 2 | Middle -> Fast | `claude-opus-5-5` / `claude-sonnet-4-6` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` | `<sonnet-id>` / `<sonnet-id>` (`--effort medium`) |
| **3 (default)** | Middle -> Top | `claude-opus-5-5` / `claude-fable-5-2` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-carbon-medium` | `<sonnet-id>` / `<opus-id>` (`--effort medium`) |
| 4 (asymmetric) | `claude`: Top -> Middle; `agy`/`kiro`: Middle -> Fast | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` | `<sonnet-id>` / `<sonnet-id>` (`--effort medium`) |

- Coordinator and worker are different roles: by default (Preset 3), the coordinator plans waves, overlap and merges on the middle tier (`Opus 5.5`, `Argon`, or Kiro `<sonnet-id>`), and each worker implements one task on the top tier (`Fable 5.2`, `Carbon`, or Kiro `<opus-id>`). Every preset runs coordinators and workers at `medium` effort.
- A worker is always of the same family as its coordinator: take the worker row whose `--kind` matches the coordinator's ([topology.md](topology.md)).
- **Two-tier `code-review` mapping**: When spawning CLI review panes via `herdr agent start` ([protocols/fallback.md](protocols/fallback.md)), `flagship` lenses use the **Top** tier and `fast/balanced` lenses use the **Middle** tier (`medium` effort on both tiers for `claude` and `agy`; `-- [--agent review-<lens>] --model <opus-id> --effort medium` for `flagship` and `-- [--agent review-<lens>] --model <sonnet-id> --effort high` for `fast/balanced` on `kiro`, omitting `--agent` for external specialists without a Kiro profile), while other `--kind` families start bare. Native in-process sub-agent tools use `"opus"` / `"sonnet"` in [protocols/claude.md](protocols/claude.md), `"pro"` / `"flash"` in [protocols/agy.md](protocols/agy.md), and synced `~/.kiro/agents/review-<lens>.md` profiles (`<opus-id>` / `<sonnet-id>` in frontmatter, inheriting session effort) in [protocols/kiro.md](protocols/kiro.md).
- Host-specific `--` flag syntax (`--model` + `--effort` on `claude`, `--model` alone on `agy`, `--agent` + `--model` + `--effort` on `kiro`, bare start on other kinds) lives in [protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), and [protocols/fallback.md](protocols/fallback.md).
- Review sub-agents or fallback review panes dispatched by a worker stay in the worker's agent family unless the person explicitly overrides it.
- The person can override the preset (1–4) or any individual row; say so in the first prompt so the worker does not assume the default.
