# Claude Code Protocol (`--kind claude`)

Host-specific mechanics for coordinators and workers running under `--kind claude`. Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "claude"`.

## 1. Startup & Model Flags

Look up `<model-id>` and `<effort>` for the role (or CLI reviewer tier) in [../agent-effort.md](../agent-effort.md) and pass both after `--`:

```bash
herdr agent start <name> --kind claude --pane <pane-id> -- --model <model-id> --effort <effort>
```

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- Claude's native session UUID is exposed in `agent_session.value` from `herdr agent list` / `herdr agent get`. Record it only when inspecting or resuming a Claude session directly; never pass a UUID as a `herdr agent` target.

## 3. Skill Invocation

- Invoke `/grill-me` and `/code-review` directly when registered as slash commands in the session.
- If a skill is not registered as a slash command, read its `SKILL.md` directly (`grill-me`, `code-review`, `herdr`) and follow its workflow inline.

## 4. Asking the Person (`AskUserQuestion` Only)

- **Always** use Claude's blocking `AskUserQuestion` tool for every question and decision confirmation with the person in your pane (place the recommended option first, prefixed with `(Recommended)`).
- **Never ask the person a question in plain prose** (this overrides standalone `grill-me`'s open-ended prose fallback inside Herdr panes; see [../grilling.md](../grilling.md)). For open-ended questions, still call `AskUserQuestion` with concrete framing options and rely on the UI's built-in free-text **Other** input so Herdr reliably transitions `agent_status` to `blocked` and rejects incoming `herdr agent prompt` calls while the dialog is open.
- Do **not** emit `[WAITING-FOR-PERSON]` under `claude` (reserved for non-blocking hosts in [fallback.md](fallback.md)).

## 5. Read-Only Review Dispatch (`code-review`)

Follow [../review.md](../review.md) and the installed `code-review` skill ([code-review/SKILL.md](../../../code-review/SKILL.md)):

1. **One fresh read-only sub-agent per active lens per round**: Dispatch via Claude's `Agent` tool (or a read-only `.claude/agents/` reviewer profile with file-write, edit, and mutating shell tools disabled), passing the canonical reviewer brief and diff inputs defined in [../review.md](../review.md) (writing `/tmp/{diff,files,delta}-<task>-r<n>.*` first if git access is sandboxed). Never fold multiple lenses into one sub-agent, and never reuse a sub-agent across rounds.
2. **Two-tier model mapping** (take each lens's tier from [code-review/SKILL.md](../../../code-review/SKILL.md) §2/§4; Claude's `Agent` tool accepts family aliases rather than versioned CLI IDs):
   - `flagship` → `model: "opus"`
   - `fast/balanced` → `model: "sonnet"`
3. **Fallback runner**: If Claude's native `Agent` tool is unavailable, run reviewers via temporary Herdr review tabs in [fallback.md](fallback.md), passing §1's `-- --model <model-id> --effort medium` flags for the CLI reviewer tier in [../agent-effort.md](../agent-effort.md) (`flagship` → Top, `fast/balanced` → Middle).
