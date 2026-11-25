# Claude Code Protocol (`--kind claude`)

Host-specific mechanics for coordinators and workers running under `--kind claude`. Loaded only when the entry for `$HERDR_PANE_ID` in `herdr agent list` has `agent == "claude"`.

## 1. Startup & Model Flags

Look up `<model-id>` and `<effort>` for the role (or CLI reviewer tier) in [../agent-effort.md](../agent-effort.md) and pass both after `--`:

```bash
herdr agent start <name> --kind claude --pane <pane-id> -- --model <model-id> --effort <effort>
```

## 2. Session Identity

- Use Herdr live agent names and pane IDs for all `herdr agent` commands ([../topology.md](../topology.md)).
- Claude's native session UUID in `agent_session.value` is internal; never pass a UUID as a `herdr agent` target.

## 3. Skill Invocation

- Invoke `/diff-review` directly when registered as a slash command, or read `diff-review`'s `SKILL.md` (`../../../diff-review/SKILL.md`) and `herdr`'s `SKILL.md` directly and follow their workflows inline.

## 4. Asking the Person (`AskUserQuestion` Only)

- **Always** use Claude's blocking `AskUserQuestion` tool for every question and confirmation with the person in your pane (including queue confirmation and formal GitHub PR review submission confirmation), placing the recommended option first prefixed with `(Recommended)`.
- **Never ask the person a question in plain prose.** Do **not** emit `[WAITING-FOR-PERSON]` under `claude`.

## 5. Read-Only `diff-review` Dispatch

Follow [../worker-review.md](../worker-review.md) and `diff-review` ([diff-review/SKILL.md](../../../diff-review/SKILL.md)):

1. **One fresh read-only sub-agent per active lens**: Dispatch via Claude's `Agent` tool (with file-write, edit, and mutating shell tools disabled), passing the lens guide, PR context, `/tmp` diff/files artifacts (`/tmp/diff-pr-<N>-r1.patch`, `/tmp/files-pr-<N>-r1.txt` when git access is sandboxed), and `diff-review`'s [reviewer-contract.md](../../../diff-review/references/reviewer-contract.md). Never combine lenses or reuse sub-agents.
2. **Two-tier model mapping** (`diff-review/SKILL.md` §2/§4):
   - `flagship` → `model: "opus"`
   - `fast/balanced` → `model: "sonnet"`
3. **Fallback runner**: If `Agent` is unavailable, run reviewers via temporary Herdr review tabs in [fallback.md](fallback.md), passing §1's `-- --model <model-id> --effort medium` flags (`flagship` → Middle, `fast/balanced` → Fast).
