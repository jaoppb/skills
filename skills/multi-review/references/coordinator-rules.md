# Coordinator rules

## 1. Spawning and monitoring workers

- Spawn one worktree and one worker per confirmed PR ([topology.md](topology.md)), including the PR number, base branch, assigned `lenses: [...]`, effort preset, coordinator pane ID, and the reference paths to read (`worker-review.md`, `reporting-protocol.md`, and the worker's host `protocols/<kind>.md`) in the worker's first prompt.
- Wait on workers with `herdr agent wait <name> --until ...` ([reporting-protocol.md](reporting-protocol.md)); never `sleep`-poll.
- Whenever a worker is `blocked` or ends its visible output with `[WAITING-FOR-PERSON]` (for example, waiting on the person to validate and confirm its drafted GitHub review), **never** answer or send keys; tell the person which pane is waiting.

## 2. Handling worker messages

- **`[TREE <pr>]`**: Update the PR's assigned `lenses: [...]` if the newly triggered lens is valid, and reply `go` so the worker can dispatch `diff-review`.
- **`[QUESTION <pr>]`**: Surface the options and recommendation to the person if it requires a human decision, then relay the answer back to the worker.
- **`[BLOCKED <pr>]`**: Inspect the blocker (e.g., missing PR access, sandbox error, merge conflict preventing clean diff) and resolve or escalate to the person.
- **`[DONE <pr>]`**: Verify the report includes PR URL, reviewed `HEAD` SHA, active `lenses`, verdict (`APPROVE` or `REQUEST_CHANGES`), finding counts, and GitHub posting status, then clean up the worker's read-only worktree ([cleanup.md](cleanup.md)).

## 3. Consolidated merge-readiness summary

Once all workers finish (or as batches complete), present a consolidated summary table to the person:

| PR | Title | Verdict | Blockers / Material | GitHub Review | Next Step |
|----|-------|---------|---------------------|---------------|-----------|

- Group **ready-to-merge** PRs (`APPROVE`, CI green, no stacked-PR blocker) separately from **needs-changes** PRs (`REQUEST_CHANGES`).
- Merging remains strictly the person's decision. For `REQUEST_CHANGES` PRs, offer to hand them off to the PR authors or spin up `multi-implement` if the person wants fixes implemented.
