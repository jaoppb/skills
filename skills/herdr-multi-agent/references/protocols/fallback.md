# Fallback Protocol (Other Herdr Kinds & CLI Review Tabs)

Host mechanics for any Herdr `--kind` without a dedicated protocol file (`codex`, `gemini`, `opencode`, `cursor`, `copilot`, `kiro`, etc.), and the fallback CLI review runner when a `claude` or `agy` worker cannot use native in-process sub-agents.

## 1. Startup & Model Flags

Start the agent with no model or effort flags unless the person explicitly requested native CLI arguments ([../agent-effort.md](../agent-effort.md)):

```bash
herdr agent start <name> --kind <kind> --pane <pane-id>
```

If the person specified explicit native flags for `<kind>`, pass them after `--`. Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).

## 2. Skill Invocation

Read each skill's `SKILL.md` file directly from disk (`grill-me`, `code-review`, `herdr`) and execute its workflow inline.

## 3. Asking the Person (`[WAITING-FOR-PERSON]` Sentinel)

Prose-only CLI hosts finish a question turn in `agent_status == idle` or `done` rather than `blocked`. Whenever a coordinator or worker on `fallback.md` asks the person a question or requests decision confirmation:

1. Ask **one** concrete question at a time (list options with `(Recommended)` first when enumerable).
2. Place the literal sentinel `[WAITING-FOR-PERSON]` **on its own final line** at the very end of the message, then stop immediately with no trailing text.
3. Never emit `[WAITING-FOR-PERSON]` on non-question turns. Workers checking `--source visible` ([../reporting-protocol.md](../reporting-protocol.md)) treat a latest turn ending in `[WAITING-FOR-PERSON]` as blocked on the person.

## 4. Read-Only Review Dispatch via Temporary Herdr Tabs (`code-review`)

When the host has no native read-only sub-agent tool, run [../review.md](../review.md) and `code-review` ([../../../code-review/SKILL.md](../../../code-review/SKILL.md)) in temporary workspace tabs:

1. **Write diff artifacts & snapshot worktree state**:
   - Write `/tmp/diff-<task>-r<n>.patch` (`git diff origin/<base>...HEAD`) and, on Round N+1, `/tmp/delta-<task>-r<n>.patch` (`git diff <prev_round_sha>..HEAD`).
   - Record `git rev-parse HEAD` and `git status --porcelain` before starting reviewers so unauthorized writes by CLI agents are caught immediately.
2. **Keep Tab 1 untouched; create up to 2 temporary review tabs (up to 4 panes each)**:
   - **Tab 1 (`$HERDR_TAB_ID`) remains exclusively for the main worker agent** — never split the worker's own tab.
   - Create up to **2** temporary tabs in `$HERDR_WORKSPACE_ID`, splitting each tab into at most **4** panes (2×2 grid: split root `right`, then split each column `down` as needed), for **at most 8 concurrent reviewers**:
     ```bash
     herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label "rev-r<n>-1" --no-focus
     herdr pane split --pane <tab-pane-id> --direction right --cwd "$PWD" --no-focus
     ```
   - Create `rev-r<n>-2` only when more than 4 lenses run in the round. If more than 8 lenses are active, run the first 8, read and close both review tabs, then run the next batch in fresh review tabs.
3. **Start one fresh reviewer agent per active lens**:
   - Name each reviewer `rev-<task>-<lens>-r<n>` (trimmed to `[a-z][a-z0-9_-]{0,31}`), using the worker's `--kind` unless overridden by the person.
   - Apply CLI tier flags from [../agent-effort.md](../agent-effort.md) when `<kind>` is `claude` or `agy`; start bare for all other kinds:
     - `claude`: `flagship` → `-- --model claude-fable-5-2 --effort medium`; `fast/balanced` → `-- --model claude-opus-5-5 --effort medium`
     - `agy`: `flagship` → `-- --model gemini-4-carbon-medium`; `fast/balanced` → `-- --model gemini-4-argon-medium`
     - Other `--kind`: `herdr agent start <rev-name> --kind <kind> --pane <pane-id>`
4. **Prompt, wait, and read (with alternate-screen fallback)**:
   - Write each lens's read-only brief (lens file path, `/tmp/diff-<task>-r<n>.patch`, Round N+1 delta + prior `fixed`/`rejected`/`deferred` ledger, severity contract `blocker`/`material`/`nitpick`/out-of-scope, and explicit **read-only: do not create, edit, or commit repository files** rule) to `/tmp/brief-rev-<task>-<lens>-r<n>.md`.
   - Submit `herdr agent prompt <rev-name> "Read /tmp/brief-rev-<task>-<lens>-r<n>.md completely and follow it."` (no `--wait`).
   - Follow [../reporting-protocol.md](../reporting-protocol.md): wait for turn start (`herdr agent wait <rev-name> --until working --timeout 15000`), then wait for completion (`herdr agent wait <rev-name> --until idle --until done --until blocked --timeout 180000`, repeating on `timeout`; if `blocked`, inspect and ask the person rather than sending keys).
   - Read findings via `herdr agent read <rev-name> --source recent-unwrapped --lines 120`. If alternate-screen TUI rendering truncates the report, prompt `<rev-name>` to write its full Markdown findings to `/tmp/rev-<task>-<lens>-r<n>.md` and reply only with the path, wait `--until working` then `--until idle --until done --until blocked`, and read `/tmp/rev-<task>-<lens>-r<n>.md`.
5. **Close temporary tabs & verify read-only integrity**:
   - Close every temporary review tab at the end of each batch/round (including on failure) with `herdr tab close <tab-id>` (or `herdr pane close <pane-id>` for an individual pane). Never close Tab 1 (`$HERDR_TAB_ID`).
   - Re-check `git rev-parse HEAD` and `git status --porcelain` (and `git diff` if needed). If any reviewer touched the worktree, fail loud: do not accept the round, restore clean state (or send `[BLOCKED <task>]` if ambiguous), and re-run the affected lens cleanly.
