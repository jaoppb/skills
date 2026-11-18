# Kiro CLI Protocol (`--kind kiro`)

Host-specific mechanics for coordinators and workers running under `--kind kiro` (`kiro-cli`). Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "kiro"`.

## 1. Coordinator Preflight (`~/.kiro/agents/` Sync)

`kiro-cli` enforces sub-agent tool restrictions (`tools: ["read"]` for read-only reviewers and `subagent` for orchestrators) through static custom agent profiles. To keep every Herdr task worktree `git status -sb` clean for [../cleanup.md](../cleanup.md) without writing untracked `.kiro/agents/` files into worktrees, `herdr-multi-agent` syncs 13 namespaced profiles (`herdr-coordinator.md`, `herdr-worker.md`, and 11 `review-<lens>.md` wrappers rendered from [../kiro-agents/herdr-coordinator.md](../kiro-agents/herdr-coordinator.md), [../kiro-agents/herdr-worker.md](../kiro-agents/herdr-worker.md), and [../kiro-agents/review-lens.md](../kiro-agents/review-lens.md)) into `~/.kiro/agents/` via [../../scripts/sync_kiro_agents.py](../../scripts/sync_kiro_agents.py).

Before spawning any `--kind kiro` workers, the coordinator runs:

```bash
python3 <skill-dir>/scripts/sync_kiro_agents.py --check
```

Handle the exit code strictly:
- **Exit `0`**: All 13 managed profiles are present, unedited, and synced to the host's current `kiro-cli` models and `code-review` lenses.
- **Exit `1` (`missing` or `stale` profiles)**: Run `python3 <skill-dir>/scripts/sync_kiro_agents.py` once to install or refresh untouched managed profiles automatically. If that run fails, stop and ask the person (ending with `[WAITING-FOR-PERSON]`).
- **Exit `1` (`error:` — missing `kiro-cli`, unavailable Opus/Sonnet tier, or missing companion `code-review` skill) or Exit `2` (hand-edited/unmanaged `herdr-*.md` or `review-*.md` conflict)**: **Never** pass `--force` or `--allow-auto-fallback` silently. Report the exact error to the person and ask whether to pass explicit `--opus-model` / `--sonnet-model`, `--allow-auto-fallback`, or `--force`, ending with `[WAITING-FOR-PERSON]`.

## 2. Startup & Model Flags

Resolve exact available Claude model slugs on the host using:

```bash
python3 <skill-dir>/scripts/sync_kiro_agents.py --print-models
```

This queries `kiro-cli chat --list-models --format json` and picks the highest semantic `claude-opus-*` and `claude-sonnet-*` slugs (preferring canonical non-dated slugs over 8-digit dated snapshots). Look up the role's tier in [../agent-effort.md](../agent-effort.md) (default Preset 3: Coordinator = Middle `<sonnet-id>`, Worker = Top `<opus-id>`, both at `medium` effort) and pass `--agent`, `--model`, and `--effort` after `--`:

```bash
# Coordinator (when launched via herdr agent start)
herdr agent start <name> --kind kiro --pane <pane-id> -- --agent herdr-coordinator --model <sonnet-id> --effort medium

# Worker
herdr agent start <name> --kind kiro --pane <pane-id> -- --agent herdr-worker --model <model-id> --effort medium
```

## 3. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- Any Kiro session identifier in `agent_session.value` from `herdr agent list` / `herdr agent get` and internal `invoke_sub_agent` calls are internal to `kiro-cli`; never pass them as `herdr agent` targets.

## 4. Skill Invocation

- Invoke `/grill-me` and `/code-review` directly when registered as slash commands, or activate/read each skill's `SKILL.md` (`grill-me`, `code-review`, `herdr`) via `disclose_context` / `read` (`read_file`) and execute its workflow inline.

## 5. Asking the Person (`[WAITING-FOR-PERSON]` Sentinel)

Because `kiro-cli` does not expose a blocking multiple-choice TUI dialog tool, Kiro turns that ask a question finish with `agent_status == idle` or `done` rather than `blocked`. Whenever a `kiro` coordinator or worker asks the person a question or requests decision confirmation (including every `grill-me` question/confirmation and any preflight prompt):

1. Ask **one** concrete question at a time in prose (list options with `(Recommended)` first when enumerable).
2. Place the literal sentinel `[WAITING-FOR-PERSON]` **on its own final line** at the very end of the message, then stop immediately with no trailing text.
3. Never emit `[WAITING-FOR-PERSON]` on non-question turns. Any peer checking `--source visible` ([../reporting-protocol.md](../reporting-protocol.md)) treats a latest turn ending in `[WAITING-FOR-PERSON]` as blocked on the person.

## 6. Read-Only Review Dispatch (`code-review`)

Follow [../review.md](../review.md) and the installed `code-review` skill ([code-review/SKILL.md](../../../code-review/SKILL.md)):

1. **Ignore managed wrappers during Open Discovery**: When scanning `.kiro/agents/` and `~/.kiro/agents/` under `code-review` §3, ignore `herdr-coordinator.md`, `herdr-worker.md`, and the 11 managed `review-<lens>.md` profiles (marked with `<!-- herdr-multi-agent-managed: ... -->` and `"not an external specialist override"`). Note that non-Kiro hosts (`claude`, `agy`, `fallback`) scanning `~/.kiro/agents/` must also ignore files carrying `herdr-multi-agent-managed` so synced Kiro wrappers never masquerade as external overrides.
2. **Write `/tmp` diff artifacts first**: Synced `review-<lens>.md` profiles enforce read-only execution structurally via pure `tools: ["read"]` (omitting `write` / `fs_write` / `fs_append` / `str_replace` / `delete_file`, `shell`, and `subagent`, with `fs_read` pre-allowed on `/tmp/**`). Because reviewers have no `shell` tool, write `/tmp/diff-<task>-r<n>.patch`, `/tmp/files-<task>-r<n>.txt`, and (on Round N+1) `/tmp/delta-<task>-r<n>.patch` before each round per [../review.md](../review.md). Never write `.kiro/agents/` files into the worktree.
3. **One fresh `subagent` (`invoke_sub_agent`) call per active lens per round**: Invoke Kiro's native `subagent` (`invoke_sub_agent`) tool in parallel targeting the synced `review-<lens>` custom agent (or a discovered read-only external `.kiro/agents/<specialist>` profile), passing the canonical reviewer brief from [../review.md](../review.md). Never combine multiple lenses into one sub-agent, and never reuse a sub-agent across rounds.
   - **Two-tier frontmatter model mapping** (synced into `~/.kiro/agents/review-<lens>.md` by `sync_kiro_agents.py`, inheriting session effort):
     - `flagship` (`code-quality`, `testing`, `security`, `data`, `performance`) → `<opus-id>`
     - `fast/balanced` (`devops`, `frontend`, `seo`, `product-owner`, `product-manager`, `api-docs`) → `<sonnet-id>`
4. **Fallback CLI review tabs**: If Kiro's native `subagent` tool is unavailable (or an external specialist lacks a read-only Kiro profile), run temporary Herdr review tabs per [fallback.md](fallback.md) §4, starting each reviewer with `--kind kiro` and explicit two-tier flags after `--`:
   - `flagship` → `-- --agent review-<lens> --model <opus-id> --effort medium`
   - `fast/balanced` → `-- --agent review-<lens> --model <sonnet-id> --effort high`
