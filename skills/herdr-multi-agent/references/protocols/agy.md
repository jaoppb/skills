# Antigravity Protocol (`--kind agy`)

Host-specific mechanics for coordinators and workers running under `--kind agy` (Antigravity CLI). Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "agy"`.

## 1. Startup & Model Flags

Look up `<model-id>` for the role (or CLI reviewer tier) in [../agent-effort.md](../agent-effort.md). Antigravity's `agy models` catalog encodes effort inside `<model-id>` (for example `gemini-4-neon-medium` for Top, `gemini-4-argon-medium` for Middle, and `gemini-4-hydrogen-medium` for Fast — inspect live IDs with `agy models`), so pass `--model` alone after `--`:

```bash
herdr agent start <name> --kind agy --pane <pane-id> -- --model <model-id>
```

`agy` also exposes an optional `--effort` flag (`low|medium|high|xhigh|max`); omit it for standard preset starts and use it only when explicitly overriding the effort suffix on a run.

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- The host conversation ID appears in `agent_session.value` from `herdr agent list` / `herdr agent get` (matching `<appDataDir>/brain/<conversation-id>`). Sub-agent `conversationId` handles returned by `invoke_subagent` are internal to Antigravity (`send_message` / `manage_subagents`) and are never passed to `herdr agent`.

## 3. Skill Invocation

- Slash commands (`/grill-me`, etc.) are user-facing chat shortcuts in Antigravity — the agent cannot execute slash commands directly.
- Always load agent-invoked skills (`grill-me`, `diff-review`, `plan-review`, `herdr`) by reading their `SKILL.md` file directly with `read_file` and executing the workflow inline.

## 4. Asking the Person (`ask_question` Only)

- **Always** use Antigravity's blocking `ask_question` tool for every question and decision confirmation with the person in your pane. Put the recommended option first, prefixed with `(Recommended)` (do not number options or add an "Other" entry manually; the UI adds both).
- **Never ask the person a question in plain prose** (this overrides standalone `grill-me`'s open-ended prose fallback inside Herdr panes; see [../grilling.md](../grilling.md)). For open-ended questions, still call `ask_question` and rely on the UI's built-in free-text **Other** input so Herdr reliably transitions `agent_status` to `blocked` and rejects incoming `herdr agent prompt` calls while waiting on the person.
- Do **not** emit `[WAITING-FOR-PERSON]` under `agy` (reserved for non-blocking hosts in [fallback.md](fallback.md)).

## 5. Read-Only Review Dispatch (`diff-review` & `plan-review`)

Follow [../review.md](../review.md) and the installed `diff-review` ([diff-review/SKILL.md](../../../diff-review/SKILL.md)) or `plan-review` ([plan-review/SKILL.md](../../../plan-review/SKILL.md)) skill:

1. **Write `/tmp` artifacts first**:
   - **`diff-review` (worktree gitfile rule)**: In Herdr git worktrees, `.git` is a gitfile pointing outside the worktree root, so sandboxed read-only sub-agents cannot run `git`. Before each round, write `/tmp/diff-<task>-r<n>.patch`, `/tmp/files-<task>-r<n>.txt`, and (on Round N+1) `/tmp/delta-<task>-r<n>.patch` (or write them under the conversation `scratch/` directory) per [../review.md](../review.md), readable via `read_file`.
   - **`plan-review`**: Pre-fetch any remote tracker issues and write `/tmp/plan-<slug>-r<n>.md` (and on Round N+1 `/tmp/plan-delta-<slug>-r<n>.diff`) per [../review.md](../review.md) so read-only sub-agents need only `/tmp` + repository read access.
2. **Define a read-only sub-agent**: Define once per conversation with write and command tools disabled:
   ```text
   define_subagent(
     Name: "specialist-reviewer",
     Description: "Read-only single-lens diff-review or plan-review specialist",
     SystemPrompt: "You are a read-only specialist reviewer. Read the assigned lens guide, pre-written /tmp diff or plan artifacts, task/spec context, and workspace files. Report findings mapped to blocker, material, nitpick, or out-of-scope. Edit nothing and run no mutating commands.",
     EnableWriteTools: false
   )
   ```
3. **One fresh `invoke_subagent` per active lens per round**: Launch one new sub-agent per active lens in parallel with the canonical reviewer brief from [../review.md](../review.md) (never reuse a prior round's `conversationId`, and never combine lenses). Map each lens's tier ([diff-review/SKILL.md](../../../diff-review/SKILL.md) §2/§4 or [plan-review/SKILL.md](../../../plan-review/SKILL.md) §2/§4) to `invoke_subagent`'s `Model` enum:
   - `flagship` → `Model: "pro"`
   - `fast/balanced` → `Model: "flash"`
4. **Reactive wakeup**: Stop calling tools after launching the round's sub-agents; Antigravity resumes automatically as each sub-agent replies (do not poll).
5. **Fallback runner**: If `define_subagent` / `invoke_subagent` is unavailable, run reviewers via temporary Herdr review tabs in [fallback.md](fallback.md), passing §1's `-- --model <model-id>` flag for the CLI reviewer tier in [../agent-effort.md](../agent-effort.md) (`flagship` → Middle, `fast/balanced` → Fast).
