# Fallback Protocol (Other Herdr Kinds & CLI Review Tabs)

Host mechanics for any Herdr `--kind` without a dedicated protocol file (`codex`, `gemini`, `opencode`, `cursor`, `copilot`, etc.), and the fallback CLI review runner when a `claude`, `agy`, or `kiro` worker cannot use native read-only sub-agents.

## 1. Startup & Model Flags

Start the agent with no model or effort flags unless the person explicitly requested native CLI arguments ([../agent-effort.md](../agent-effort.md)):

```bash
herdr agent start <name> --kind <kind> --pane <pane-id>
```

Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).

## 2. Skill Invocation

Read `diff-review/SKILL.md` (`../../../diff-review/SKILL.md`) and `herdr/SKILL.md` directly from disk and execute their workflows inline.

## 3. Asking the Person (`[WAITING-FOR-PERSON]` Sentinel)

Prose-only CLI hosts finish a question turn in `agent_status == idle` or `done` rather than `blocked`. Whenever a coordinator or worker on `fallback.md` asks the person a question or requests confirmation (queue confirmation or formal GitHub PR review submission):

1. Ask **one** concrete question at a time (list options with `(Recommended)` first when enumerable).
2. Place `[WAITING-FOR-PERSON]` **on its own final line** at the very end of the message, then stop immediately with no trailing text.
3. Never emit `[WAITING-FOR-PERSON]` on non-question turns.

## 4. Read-Only `diff-review` Dispatch via Temporary Herdr Tabs

When the host has no native read-only sub-agent tool, run [../worker-review.md](../worker-review.md) with `diff-review` in temporary workspace tabs:

1. **Write `/tmp` artifacts & snapshot worktree state**: Write `/tmp/diff-pr-<N>-r1.patch` and `/tmp/files-pr-<N>-r1.txt`. Record `git rev-parse HEAD` and `git status --porcelain` before starting reviewers.
2. **Keep Tab 1 untouched; create up to 2 temporary review tabs (up to 4 panes each)**:
   - Never split the worker's own tab (`$HERDR_TAB_ID`).
   - Create up to 2 temporary tabs (`rev-r1-1`, `rev-r1-2` if >4 lenses) in `$HERDR_WORKSPACE_ID` with at most 4 panes each (2×2 grid via `herdr tab create` and `herdr pane split --no-focus`), for at most 8 concurrent reviewers. Batch if >8 lenses are active.
3. **Start one fresh reviewer per active lens**: Name each `rev-pr<N>-<lens>` matching `[a-z][a-z0-9_-]{0,31}` (shortening `<lens>` if needed while keeping uniqueness). Pass `--` startup flags from the active protocol for the lens's tier in [../agent-effort.md](../agent-effort.md) (`flagship` → Middle, `fast/balanced` → Fast), or start bare for fallback kinds.
4. **Prompt, wait, and read**: Write the reviewer brief to `/tmp/brief-<rev-name>.md`, submit `herdr agent prompt <rev-name> "Read /tmp/brief-<rev-name>.md completely and follow it."` (no `--wait`), wait per [../reporting-protocol.md](../reporting-protocol.md) (`--until working` then `--until idle --until done --until blocked --timeout 180000`), and read via `herdr agent read <rev-name> --source recent-unwrapped --lines 120` (falling back to `/tmp/<rev-name>.md` if TUI rendering truncates).
5. **Close temporary tabs & verify read-only integrity**: Close every temporary review tab with `herdr tab close <tab-id>` (never close Tab 1). Re-check `git rev-parse HEAD` and `git status --porcelain`; if any reviewer modified files, fail loud, restore clean state, and re-run that lens cleanly.
