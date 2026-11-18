# Antigravity Protocol (`--kind agy`)

Host-specific mechanics for coordinators and workers running under `--kind agy` (Antigravity CLI). Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "agy"`.

## 1. Startup & Model Flags

Look up the role's model from the active preset in [../agent-effort.md](../agent-effort.md) (default **Preset 3**: coordinator `gemini-4-argon-medium`, worker `gemini-4-carbon-medium`). Antigravity encodes effort inside the model ID (inspect available IDs with `agy models`), so pass `--model` after `--` with **no** `--effort` flag:

```bash
# Coordinator (Preset 3 default)
herdr agent start <name> --kind agy --pane <pane-id> -- --model gemini-4-argon-medium

# Worker (Preset 3 default)
herdr agent start <name> --kind agy --pane <pane-id> -- --model gemini-4-carbon-medium
```

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- The host conversation ID appears in `agent_session.value` from `herdr agent list` / `herdr agent get` (matching `<appDataDir>/brain/<conversation-id>`). Sub-agent `conversationId` handles returned by `invoke_subagent` are internal to Antigravity (`send_message` / `manage_subagents`) and are never passed to `herdr agent`.

## 3. Skill Invocation

- Slash commands (`/grill-me`, etc.) are user-facing chat shortcuts in Antigravity — the agent cannot execute slash commands directly.
- Always load agent-invoked skills (`grill-me`, `code-review`, `herdr`) by reading their `SKILL.md` file directly with `read_file` and executing the workflow inline.

## 4. Asking the Person (`ask_question` Only)

- **Always** use Antigravity's blocking `ask_question` tool for every question and decision confirmation with the person in your pane. Put the recommended option first, prefixed with `(Recommended)` (do not number options or add an "Other" entry manually; the UI adds both).
- **Never ask the person a question in plain prose.** For open-ended questions, still call `ask_question` and rely on the UI's built-in free-text **Other** input so Herdr reliably transitions `agent_status` to `blocked` and rejects incoming `herdr agent prompt` calls while waiting on the person.
- Do **not** emit `[WAITING-FOR-PERSON]` under `agy` (reserved for non-blocking hosts in [fallback.md](fallback.md)).

## 5. Read-Only Review Dispatch (`code-review`)

Follow [../review.md](../review.md) and the installed `code-review` skill ([../../../code-review/SKILL.md](../../../code-review/SKILL.md)):

1. **Write diff artifacts before dispatching (worktree gitfile rule)**: In Herdr git worktrees, `.git` is a gitfile pointing outside the worktree root, so sandboxed read-only sub-agents cannot run `git` commands. Before each round, the worker writes:
   - `/tmp/diff-<task>-r<n>.patch` (`git diff origin/<base>...HEAD`)
   - `/tmp/files-<task>-r<n>.txt` (`git diff --name-only origin/<base>...HEAD`)
   - On Round N+1: `/tmp/delta-<task>-r<n>.patch` (`git diff <prev_round_sha>..HEAD`)
   (Using `/tmp` or the conversation `scratch/` directory, both readable by sandboxed sub-agents via `read_file`.)
2. **Define a read-only sub-agent**: Define a reviewer sub-agent type once per conversation with write tools disabled:
   ```text
   define_subagent(
     Name: "code-reviewer",
     Description: "Read-only single-lens code-review specialist",
     SystemPrompt: "You are a read-only code reviewer. Read the assigned lens guide, diff files, and repository files. Report findings mapped to blocker, material, nitpick, or out-of-scope. Edit nothing.",
     EnableWriteTools: false
   )
   ```
3. **One fresh `invoke_subagent` per active lens per round**: Launch a new sub-agent per active lens in parallel (never message a prior round's `conversationId` to re-review, and never fold two lenses into one sub-agent), mapping `code-review` tiers as follows:
   - `flagship` lenses (`code-quality`, `testing`, `security`, `data`, `performance`, and deep-tagged external specialists) → `Model: "pro"`
   - `fast/balanced` lenses (`frontend`, `seo`, `devops`, `product-owner`, `product-manager`, `api-docs`, and external specialists by default) → `Model: "flash"`
4. **Sub-agent brief & reactive wakeup**: Pass each sub-agent its lens file path, `/tmp/diff-<task>-r<n>.patch` (plus `/tmp/delta-<task>-r<n>.patch` and that lens's prior `fixed` / `rejected` / `deferred` ledger on Round N+1), and task context. Stop calling tools after launching the round's sub-agents; Antigravity resumes automatically as each sub-agent replies (do not poll).
5. **Fallback runner**: If `define_subagent` / `invoke_subagent` is unavailable, run reviewers via temporary Herdr review tabs in [fallback.md](fallback.md).
