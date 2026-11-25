# Antigravity Protocol (`--kind agy`)

Host-specific mechanics for coordinators and workers running under `--kind agy` (Antigravity CLI). Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "agy"`.

## 1. Startup & Model Flags

Look up `<model-id>` for the role (or CLI reviewer tier) in [../agent-effort.md](../agent-effort.md) (Antigravity encodes effort in `<model-id>`, e.g. `gemini-4-argon-medium` for Middle and `gemini-4-hydrogen-medium` for Fast):

```bash
herdr agent start <name> --kind agy --pane <pane-id> -- --model <model-id>
```

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- `agent_session.value` and `invoke_subagent` `conversationId` handles are internal to Antigravity; never pass them to `herdr agent`.

## 3. Skill Invocation

- Slash commands (`/diff-review`, etc.) cannot be executed directly by the agent in Antigravity. Always read `diff-review/SKILL.md` (`../../../diff-review/SKILL.md`) and `herdr/SKILL.md` with `read_file` and execute inline.

## 4. Asking the Person (`ask_question` Only)

- **Always** use Antigravity's blocking `ask_question` tool for every question and confirmation with the person in your pane (including queue confirmation and formal GitHub PR review submission confirmation). Put the recommended option first, prefixed with `(Recommended)` (do not number options or add an "Other" entry manually; the UI adds both).
- **Never ask the person a question in plain prose.** Do **not** emit `[WAITING-FOR-PERSON]` under `agy`.

## 5. Read-Only `diff-review` Dispatch

Follow [../worker-review.md](../worker-review.md) and `diff-review` ([diff-review/SKILL.md](../../../diff-review/SKILL.md)):

1. **Write `/tmp` artifacts first**: In Herdr git worktrees, `.git` is a gitfile pointing outside the worktree root, so sandboxed read-only sub-agents cannot run `git`. Write `/tmp/diff-pr-<N>-r1.patch` and `/tmp/files-pr-<N>-r1.txt` before dispatching.
2. **Define a read-only sub-agent**:
   ```text
   define_subagent(
     Name: "specialist-reviewer",
     Description: "Read-only single-lens diff-review specialist",
     SystemPrompt: "You are a read-only specialist reviewer. Read the assigned lens guide, pre-written /tmp diff artifacts, PR context, and workspace files. Report findings mapped to blocker, material, nitpick, or out-of-scope. Edit nothing and run no mutating commands.",
     EnableWriteTools: false
   )
   ```
3. **One fresh `invoke_subagent` per active lens in parallel**: Never combine lenses. Map each lens's tier (`diff-review/SKILL.md` §2/§4) to `invoke_subagent`'s `Model` enum:
   - `flagship` → `Model: "pro"`
   - `fast/balanced` → `Model: "flash"`
4. **Reactive wakeup**: Stop calling tools after launching the sub-agents; Antigravity resumes automatically as each replies (do not poll).
5. **Fallback runner**: If `define_subagent` / `invoke_subagent` is unavailable, run temporary Herdr review tabs in [fallback.md](fallback.md), passing §1's `-- --model <model-id>` flag (`flagship` → Middle, `fast/balanced` → Fast).
