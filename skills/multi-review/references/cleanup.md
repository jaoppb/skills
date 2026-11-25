# Cleaning up finished review worktrees

Reviewer worktrees are strictly read-only, so once a worker reports `[DONE <pr>]` and the coordinator has recorded its summary, the coordinator may clean up the finished review worktree without asking.

1. **Verify clean read-only state before removing**:
   - `git status -sb` inside the worktree must show no uncommitted or untracked changes.
   - Confirm no unpushed local branch commits were created (HEAD should be the detached PR `FETCH_HEAD` or clean at `<baseRefName>`).
2. **Remove proven worktrees one at a time**:
   ```bash
   herdr worktree remove --workspace <id>
   ```
   Do **not** pass `--force`. Removing the workspace removes the worktree directory along with all tabs, panes, and agents inside it (including any leftover temporary review tabs from [protocols/fallback.md](protocols/fallback.md)).
3. **Keep anything dirty or incomplete**: If `git status -sb` is dirty or the worker exited before `[DONE <pr>]`, leave the worktree intact and report it to the person.
4. **Temporary review branches**: If any local `review/pr-<N>` placeholder branch was created for worktree setup, delete it after `herdr worktree remove` (`git branch -D review/pr-<N>`) only if its tip is at `<baseRefName>` (`ahead_by` 0). Never delete PR author branches or unrelated local branches.
