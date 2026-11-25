# Topology

1. **One Herdr worktree per PR**, created from the **primary** workspace (the repo parent, not a linked worktree; find the primary with `herdr worktree list`, field `source_workspace_id`):
   ```bash
   herdr worktree create --workspace <primary> --branch review/pr-<N> --base <baseRefName> --label review-pr-<N> --no-focus
   ```
   Inside the worktree, the worker immediately checks out the PR head detached (`git fetch origin pull/<N>/head && git checkout --detach FETCH_HEAD`) per [worker-review.md](worker-review.md) so it never modifies or pushes to any branch.
2. **One agent per worktree pane**: `herdr agent start <name> --kind <kind> --pane <pane-id> [-- <protocol-start-args>]`. Auto-detect the coordinator's agent kind from `herdr agent list` (matching `$HERDR_PANE_ID`, e.g. `claude`, `agy`, `kiro`, `codex`, `gemini`), and default `--kind` to that unless the person asked for a different kind. Load the matching protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), or [protocols/fallback.md](protocols/fallback.md)), select the worker model from [agent-effort.md](agent-effort.md), and pass any `--` startup flags defined by that protocol.
3. **Startup recovery**: If `herdr agent start` fails with `timed out waiting for agent startup`, read the pane (`herdr pane read <pane> --source visible`) to verify the shell is at a clean prompt, then retry with `--timeout 90000`.
4. **Names and IDs**: Use Herdr live agent names (`rev-pr-<N>`, matching `[a-z][a-z0-9_-]{0,31}`) and pane IDs for all `herdr agent` commands. Host-native session IDs (`agent_session.value`) are internal to the host protocol.
