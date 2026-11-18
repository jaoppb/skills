# Claude Code Protocol (`--kind claude`)

Host-specific mechanics for coordinators and workers running under `--kind claude`. Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "claude"`.

## 1. Startup & Model Flags

Look up the role's model and effort from the active preset in [../agent-effort.md](../agent-effort.md) (default **Preset 3**: coordinator `claude-opus-5-5`, worker `claude-fable-5-2`, both at `medium` effort) and pass them after `--`:

```bash
# Coordinator (Preset 3 default)
herdr agent start <name> --kind claude --pane <pane-id> -- --model claude-opus-5-5 --effort medium

# Worker (Preset 3 default)
herdr agent start <name> --kind claude --pane <pane-id> -- --model claude-fable-5-2 --effort medium
```

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- Claude's native session UUID is exposed in `agent_session.value` from `herdr agent list` / `herdr agent get`. Record it only when inspecting or resuming a Claude session directly; never pass a UUID as a `herdr agent` target.

## 3. Skill Invocation

- Invoke `/grill-me` and `/code-review` directly when registered as slash commands in the session.
- If a skill is not registered as a slash command, read its `SKILL.md` directly (`grill-me`, `code-review`, `herdr`) and follow its workflow inline.

## 4. Asking the Person (`AskUserQuestion` Only)

- **Always** use Claude's blocking `AskUserQuestion` tool for every question and decision confirmation with the person in your pane (place the recommended option first, prefixed with `(Recommended)`).
- **Never ask the person a question in plain prose.** For open-ended questions, still call `AskUserQuestion` with concrete framing options and rely on the UI's built-in free-text **Other** input so Herdr reliably transitions `agent_status` to `blocked` and rejects incoming `herdr agent prompt` calls while the dialog is open.
- Do **not** emit `[WAITING-FOR-PERSON]` under `claude` (reserved for non-blocking hosts in [fallback.md](fallback.md)).

## 5. Read-Only Review Dispatch (`code-review`)

Follow [../review.md](../review.md) and the installed `code-review` skill ([../../../code-review/SKILL.md](../../../code-review/SKILL.md)):

1. **One fresh read-only sub-agent per active lens per round**: Dispatch via Claude's `Agent` tool (or a read-only `.claude/agents/` reviewer profile with file-write, edit, and mutating shell tools disabled). Never fold multiple lenses into one sub-agent, and never reuse a sub-agent across rounds.
2. **Two-tier model mapping**:
   - `flagship` lenses (`code-quality`, `testing`, `security`, `data`, `performance`, and deep-tagged external specialists) → `model: "opus"`
   - `fast/balanced` lenses (`frontend`, `seo`, `devops`, `product-owner`, `product-manager`, `api-docs`, and external specialists by default) → `model: "sonnet"`
3. **Sub-agent brief**: Give each reviewer:
   - Its single lens guide path (`references/lenses/<lens>.md` from `code-review`, or the discovered external specialist file).
   - Strict read-only rule (**report findings only; edit nothing and run no mutating commands**) and the severity contract (`blocker` / `material` / `nitpick` / out-of-scope).
   - The branch diff (`git diff origin/<base>...HEAD`, or a written `/tmp/diff-<task>-r<n>.patch` file if sandboxed git access is restricted), plus on Round N+1 the delta (`git diff <prev_round_sha>..HEAD`) and that lens's prior `fixed` / `rejected` / `deferred` ledger.
4. **Fallback runner**: If Claude's native `Agent` tool is unavailable in the environment, run reviewers via temporary Herdr review tabs in [fallback.md](fallback.md).
