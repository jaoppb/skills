# Review until approved

Every worker's branch diff is reviewed by fresh read-only specialist reviewers under the installed `code-review` skill ([code-review/SKILL.md](../../code-review/SKILL.md)) before the coordinator merges anything. This is a smart delta loop, not a fixed number of rounds.

## The loop (worker)

1. **Verify `lenses: [code-quality, ...]` before dispatching**: When implementation is done and the project's check passes, check the branch diff (`git diff origin/<base>...HEAD`) against the built-in triggers and discovered project/user specialist agents in the installed `code-review` skill ([code-review/SKILL.md](../../code-review/SKILL.md)). The coordinator owns `lenses: [code-quality, ...]` (`code-quality` is always explicit). If the diff triggers **any** lens not in the task's assigned `lenses`, stop, send `[TREE <task>]` naming the newly triggered lens(es) and files, and wait for the coordinator to update `lenses` and re-check wave overlap before running or finishing review; never self-retag.
2. **Dispatch one fresh read-only reviewer per active lens**: Follow your host protocol ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), or [protocols/fallback.md](protocols/fallback.md) temporary Herdr review tabs when native sub-agents are unavailable) to dispatch one fresh read-only reviewer per active lens in parallel using two-tier model mapping (`flagship` vs `fast/balanced`). The worker never reviews its own diff and never folds multiple lenses into one reviewer. UI tasks (`frontend` lens) delegate directly to `references/lenses/frontend.md` of the installed `code-review` skill ([frontend.md](../../code-review/references/lenses/frontend.md)): run Impeccable `audit` when installed/initialized, otherwise fall back to `frontend.md`'s built-in UI/WCAG checklist without sending `[BLOCKED]`.
3. **Fix & run smart delta re-runs**: Record `prev_round_sha = HEAD` and per-lens `fixed` / `rejected` / `deferred` findings in a temporary ledger under `/tmp` (or session scratch; never commit it). After fixing real findings in a new commit (preserving the parent reference) and re-running the project check, Round N+1 re-runs **only** `code-quality`, any lens that rejected in Round N, and any lens whose domain files changed in `git diff <prev_round_sha>..HEAD` ([code-review/SKILL.md](../../code-review/SKILL.md)). If a fix commit newly triggers an unassigned lens, send `[TREE <task>]` and wait for coordinator retag before completing review.
4. **Approval bar**: A round **approves** only when every active lens returns **zero `blocker` (P0) and zero `material` (P1) findings**. What may remain: `nitpick` (P2/P3) items rejected with a written reason, and out-of-scope items deferred with a written reason.
5. **Escalation & conflicts**: No fixed round count. After five rounds without approval, when a finding needs a decision outside the worker's scope, or when two lenses demand contradictory changes, stop and send `[QUESTION <task>]` with both positions/options and a recommendation instead of picking silently or looping on.
6. **Post-approval commits**: Any commit made after approval (rebase conflict resolution, CI fix, PR review comment) requires another delta round before the approval holds.

## The report and pull request

Once approved and project checks pass, the worker automatically pushes the branch (`git push -u origin <branch>`) and creates the pull request using `gh pr create`.

`[DONE <task>]` carries the PR URL, branch, approved HEAD commit, check result, and a Review paragraph ("Review: approved in round N") reporting per-lens round counts and fixed, rejected (with reason), and deferred (with reason) summaries. A `[DONE]` without an approved review or PR link is not ready.

## The coordinator

- Check the PR and claim: verify with `gh pr view`, confirm the approved HEAD matches the PR commit, and verify all assigned `lenses` are accounted for in the `[DONE]` summary.
- Monitor CI checks until green, then present the pull request to the person for merge authorization. Merging remains strictly the person's decision. If CI fails, the worker fixes it and, if code changed, runs another delta review round.
- Put this rule and the task's `lenses: [code-quality, ...]` in every worker's first prompt (see [worker-prompts.md](worker-prompts.md)), in the task brief even when the brief is a file.
