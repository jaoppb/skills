# Kiro CLI Protocol (`--kind kiro`)

Host-specific mechanics for coordinators and workers running under `--kind kiro` (`kiro-cli`). Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "kiro"`.

## 1. Startup & Model Flags

Resolve available Claude model slugs (`<opus-id>`, `<sonnet-id>`) via `kiro-cli chat --list-models --format json`, look up the role's tier in [../agent-effort.md](../agent-effort.md) (default Preset 2: Coordinator = `<sonnet-id>`, Worker = `<sonnet-id>`, both `--effort medium`), and start with `chat` after `--`:

```bash
herdr agent start <name> --kind kiro --pane <pane-id> -- chat --model <model-id> --effort medium
```

If synced `~/.kiro/agents/diff-review-<lens>.md` profiles exist on the host, pass `--agent <profile>` only for those read-only reviewer profiles; never write `.kiro/agents/` files inside a PR review worktree so `git status -sb` stays clean ([../cleanup.md](../cleanup.md)).

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- Kiro session IDs in `agent_session.value` and internal `invoke_sub_agent` handles are internal to `kiro-cli`.

## 3. Skill Invocation

- Invoke `/diff-review` directly when registered, or read `diff-review/SKILL.md` (`../../../diff-review/SKILL.md`) and `herdr/SKILL.md` via `disclose_context` / `read` and follow inline.

## 4. Asking the Person (`[WAITING-FOR-PERSON]` Sentinel)

Because `kiro-cli` does not expose a blocking multiple-choice dialog tool, turns that ask a question finish with `agent_status == idle` or `done`:

1. Ask **one** concrete question at a time in prose (list options with `(Recommended)` first when enumerable, e.g., confirming the triaged queue or confirming a drafted GitHub PR review).
2. Place `[WAITING-FOR-PERSON]` **on its own final line** at the very end of the message, then stop immediately with no trailing text.
3. Never emit `[WAITING-FOR-PERSON]` on non-question turns.

## 5. Read-Only `diff-review` Dispatch

Follow [../worker-review.md](../worker-review.md) and `diff-review` ([diff-review/SKILL.md](../../../diff-review/SKILL.md)):

1. **Write `/tmp` artifacts first**: Write `/tmp/diff-pr-<N>-r1.patch` and `/tmp/files-pr-<N>-r1.txt` before dispatching.
2. **Native read-only `subagent` (`invoke_sub_agent`)**: If read-only `diff-review-<lens>` profiles exist in `~/.kiro/agents/`, invoke one fresh `subagent` per active lens in parallel (and ignore managed `diff-review-*` / `plan-review-*` / `multi-implement-*` profiles during Open Discovery).
3. **Fallback CLI review tabs**: If read-only `subagent` profiles are not present or an external specialist lacks a read-only profile, run temporary Herdr review tabs per [fallback.md](fallback.md) §4 (`flagship` → `-- chat --model <sonnet-id> --effort high`; `fast/balanced` → `-- chat --model <sonnet-id> --effort medium`), verifying `git status --porcelain` stays clean.
