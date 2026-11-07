# Review until approved

Every worker's work is reviewed by sub-agents before the coordinator merges anything. This is a loop, not a fixed number of rounds.

## The loop (worker)

1. When the work is done and the project's check passes, the worker starts a round: a **new** sub-agent dispatched via the host's native capability (`Agent` tool in Claude, `invoke_subagent` in Antigravity) runs `/thermo-nuclear-code-quality-review` (or loads `skills/thermo-nuclear-code-quality-review/SKILL.md`) on the branch diff (`git diff origin/<base>..HEAD`). It is given the findings of the earlier rounds (fixed, rejected, deferred) so it looks for what is new. The worker never reviews its own diff itself and never reuses a sub-agent. If the task is tagged `ui: yes`, the round also runs the front-end lens: [review-frontend.md](review-frontend.md). If a `ui: no` task's diff turns out to touch UI files, send `[TREE <task>]` asking the coordinator to retag; never retag it yourself.
2. The worker fixes the real findings inside its own task (a new commit that keeps the parent reference), re-runs the check, and starts the next round with another new sub-agent.
3. The review **approves** when a round returns no blocker and no material finding. What may remain: nitpicks the worker rejects with a reason, and items that belong to another task, deferred with a reason.
4. No fixed round count. After five rounds without an approval, or when a finding needs a decision that is not the worker's, the worker sends `[QUESTION <task>]` with options and a recommendation instead of looping on.
5. A commit made after an approval (a rebase conflict fix, a review comment on the PR) needs another round.

## The report and pull request

Once approved and project checks pass, the worker automatically pushes the branch (`git push -u origin <branch>`) and creates the pull request using `gh pr create`.

`[DONE <task>]` carries the PR URL, branch, approved HEAD commit, and a Review paragraph: "Review: approved in round N", findings fixed, rejected, and deferred per round. A `[DONE]` without an approved review or PR link is not ready.

## The coordinator

- Check the PR and claim: verify with `gh pr view` and check that the approved HEAD matches the PR commit.
- Monitor CI checks until green, then present the pull request to the person for merge authorization. Merging remains strictly the person's decision. If CI fails, the worker fixes it and, if code changed, runs another review round.
- Put this rule in every worker's first prompt (see [worker-prompts.md](worker-prompts.md)), in the task brief even when the brief is a file.
