# Worker PR review workflow

Each worker reviews **one assigned PR** in an isolated, strictly read-only worktree. Workers do **not** run `grill-me` at startup and do **not** modify PR code or push commits.

## 1. Check out the PR read-only

From the worker's assigned Herdr worktree (created at `baseRefName` or `main`):

```bash
git fetch origin pull/<N>/head
git checkout --detach FETCH_HEAD
git fetch origin <baseRefName>
```

- Using `pull/<N>/head` works for both same-repository and fork PRs without colliding with local branch names.
- Never edit tracked files, stage changes, or commit inside the worktree. Record `PR_HEAD=$(git rev-parse HEAD)` and verify `git status --porcelain` is empty before and after review.

## 2. Verify `lenses` before dispatching `diff-review`

Compare `git diff --name-only origin/<baseRefName>...HEAD` against `diff-review`'s content-aware baseline, conditional triggers, and discovered project/user external specialists (`diff-review/SKILL.md`).

- If the diff triggers any lens (including a missing baseline) not in the coordinator's assigned `lenses`, send `[TREE <pr>]` naming the newly triggered lens(es) and files, and wait for the coordinator to confirm the updated `lenses` before running review.

## 3. Run single-pass multi-lens `diff-review`

Follow your host protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), or [protocols/fallback.md](protocols/fallback.md)) and `diff-review/SKILL.md`:

- Dispatch **one fresh read-only reviewer per active lens in parallel** using two-tier model mapping (`flagship` vs `fast/balanced`, [agent-effort.md](agent-effort.md)). Never review your own diff and never combine multiple lenses into one reviewer.
- Whenever git is sandboxed in a worktree or reviewers run in temporary CLI tabs, write `/tmp/diff-pr-<N>-r1.patch` (`git diff origin/<baseRefName>...HEAD`) and `/tmp/files-pr-<N>-r1.txt` (`git diff --name-only origin/<baseRefName>...HEAD`) before dispatching.
- Pass every reviewer its single lens guide, the PR metadata/description (`gh pr view <N>`), the diff and changed-file list, and `diff-review`'s shared `references/reviewer-contract.md`.

## 4. Aggregate findings and determine verdict

Use `diff-review`'s canonical severities (`blocker`, `material`, `nitpick`, `out-of-scope`):

- **`APPROVE`**: Zero `blocker` (P0) and zero `material` (P1) findings across all active lenses. `nitpick` and `out-of-scope` items may be included as non-blocking notes.
- **`REQUEST_CHANGES`**: One or more `blocker` or `material` findings.

Verify every finding against the actual PR diff (`git diff origin/<baseRefName>...HEAD`) so line numbers, file paths, and hunk positions are accurate before drafting GitHub comments.

## 5. Draft, display, and confirm the formal GitHub review

1. **Draft** the formal review:
   - Overall review status: `APPROVE` or `REQUEST_CHANGES`.
   - Concise top-level review body summarizing the verdict and key findings.
   - Inline diff comments anchored to exact `(path, line, side: "RIGHT")` positions in the PR diff for every actionable `blocker` and `material` finding (and any high-value `nitpick` worth surfacing), including the rationale and concrete fix suggestion.
2. **Display** the full drafted review—status, summary body, every inline comment (`file:line`), and its rationale—directly to the person in your pane so they can validate the reasoning.
3. **Ask for explicit confirmation** via the host's ask tool (`AskUserQuestion` / `ask_question`, or `[WAITING-FOR-PERSON]` on `kiro`/`fallback`) before posting to GitHub. Offer clear choices: post as drafted, adjust/edit before posting, or report locally without posting to GitHub.
4. **Post only if confirmed**:
   - If the review has inline comments, submit via `gh api repos/<owner>/<repo>/pulls/<N>/reviews` with `commit_id: <PR_HEAD>`, `event: "APPROVE" | "REQUEST_CHANGES"`, `body`, and `comments[]`.
   - If there are no inline comments, `gh pr review <N> --approve --body "..."` or `gh pr review <N> --request-changes --body "..."` may be used.

## 6. Report `[DONE <pr>]`

Send `[DONE <pr>]` to the coordinator ([reporting-protocol.md](reporting-protocol.md)) with:
- PR URL, reviewed `HEAD` SHA, and active `lenses`
- Verdict (`APPROVE` or `REQUEST_CHANGES`)
- Per-lens finding counts (`blocker`, `material`, `nitpick`, `out-of-scope`) and a short summary of key findings
- GitHub submission status (`posted` with review URL, or `local-only` if the person declined posting)
