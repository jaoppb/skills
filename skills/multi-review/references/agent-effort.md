# Agent and effort map

Single source of truth for coordinator and reviewer worker model tiers and selectable presets. Pair the chosen preset row with your host protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), or [protocols/fallback.md](protocols/fallback.md)) in [topology.md](topology.md).

## Default (Preset 2: Coordinator = Middle, Worker = Fast)

| Role | Family (`--kind`) | Agent | Effort | Protocol |
|------|-------------------|-------|--------|----------|
| Coordinator | `claude` | Claude Opus 5.5 (`claude-opus-5-5`) | medium | [protocols/claude.md](protocols/claude.md) |
| Coordinator | `agy` | Gemini 4 Argon (`gemini-4-argon-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Coordinator | `kiro` | Claude Sonnet (`<sonnet-id>` via `kiro-cli`) | medium | [protocols/kiro.md](protocols/kiro.md) |
| Worker | `claude` | Claude Sonnet 5.5 (`claude-sonnet-5-5`) | medium | [protocols/claude.md](protocols/claude.md) |
| Worker | `agy` | Gemini 4 Hydrogen (`gemini-4-hydrogen-medium`) | medium | [protocols/agy.md](protocols/agy.md) |
| Worker | `kiro` | Claude Sonnet (`<sonnet-id>` via `kiro-cli`) | medium | [protocols/kiro.md](protocols/kiro.md) |
| Coordinator / Worker | other `--kind` | Host default (bare start) | host default | [protocols/fallback.md](protocols/fallback.md) |

## Selectable presets

Model tiers from highest to lowest (`medium` effort by default; `agy` encodes effort in the model ID; `<opus-id>` and `<sonnet-id>` on `kiro` are the newest `claude-opus-*` and `claude-sonnet-*` slugs from `kiro-cli chat --list-models --format json`):

- **Top:** `Claude Fable 5.2` (`claude-fable-5-2`) / `Gemini 4 Neon` (`gemini-4-neon-medium`) / Kiro `claude-opus-*` (`<opus-id>`)
- **Middle:** `Claude Opus 5.5` (`claude-opus-5-5`) / `Gemini 4 Argon` (`gemini-4-argon-medium`) / Kiro `claude-sonnet-*` (`<sonnet-id>`)
- **Fast:** `Claude Sonnet 5.5` (`claude-sonnet-5-5`) / `Gemini 4 Hydrogen` (`gemini-4-hydrogen-medium`) / Kiro `claude-sonnet-*` (`<sonnet-id>`)

**Preset 2** is the default. **Top is opt-in** (Preset 3 only for unusually large or high-risk PRs):

| Preset | Coordinator -> Worker | `claude` (Coordinator / Worker) | `agy` (Coordinator / Worker) | `kiro` (Coordinator / Worker) |
|--------|-----------------------|---------------------------------|------------------------------|-------------------------------|
| 1 | Top -> Middle | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-neon-medium` / `gemini-4-argon-medium` | `<opus-id>` / `<sonnet-id>` (`--effort medium`) |
| **2 (default)** | Middle -> Fast | `claude-opus-5-5` / `claude-sonnet-5-5` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` | `<sonnet-id>` / `<sonnet-id>` (`--effort medium`) |
| 3 (opt-in Top) | Middle -> Top | `claude-opus-5-5` / `claude-fable-5-2` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-neon-medium` | `<sonnet-id>` / `<opus-id>` (`--effort medium`) |
| 4 (asymmetric) | `claude`: Top -> Middle; `agy`/`kiro`: Middle -> Fast | `claude-fable-5-2` / `claude-opus-5-5` (`--effort medium`) | `gemini-4-argon-medium` / `gemini-4-hydrogen-medium` | `<sonnet-id>` / `<sonnet-id>` (`--effort medium`) |

## Two-tier `diff-review` lens mapping

- **Native sub-agents**: Map each active lens's tier (`diff-review/SKILL.md` §2/§4) to `"opus"` / `"sonnet"` ([protocols/claude.md](protocols/claude.md)), `"pro"` / `"flash"` ([protocols/agy.md](protocols/agy.md)), or `~/.kiro/agents/diff-review-<lens>.md` profiles via `invoke_sub_agent` when present ([protocols/kiro.md](protocols/kiro.md)).
- **Fallback CLI review tabs**: `flagship` lenses use **Middle** (`--model claude-opus-5-5 --effort medium`, `--model gemini-4-argon-medium`, or `kiro` `chat --model <sonnet-id> --effort high`) and `fast/balanced` lenses use **Fast** (`--model claude-sonnet-5-5 --effort medium`, `--model gemini-4-hydrogen-medium`, or `kiro` `chat --model <sonnet-id> --effort medium`); other `--kind` families start bare.
