---
name: herdr-multi-agent
description: "Coordinate several autonomous coding agents (Claude, Antigravity, and others) through Herdr: one worktree and one agent per task, every agent starting with a grill-me session, a coordinator that always plans the tasks in waves to avoid conflicts, review by sub-agents until approved before any merge, a tagged reporting protocol and a go/hold rule. Use only when the user asks to start, organize or coordinate multiple agents or worktrees with Herdr, alongside the herdr skill. Requires HERDR_ENV=1."
---

# Herdr multi-agent coordination

Lessons from running a coordinator agent and several worker agents, one per task, each in its own Herdr worktree. Load the `herdr` skill first for the CLI itself; this skill is the working method on top of it. The details live in the reference files linked below; read the one that matches the step you are on.

## Roles

- **Coordinator** (the session that owns the whole effort): owns the task tree, shared documents, dependency order, the wave plan and the people-facing decisions. It does not implement the workers' tasks.
- **Worker** (one per task): owns one task and only the artifacts of that task (for example its own issue body or its own branch). It never edits the coordinator's artifacts, another worker's artifacts, the parent, dependency links or planning fields; it asks the coordinator.
- **The person** decides merges, permissions, and major scope changes. Pull request creation is automated once a worker's review approves. Workers rebase, push, and open PRs automatically; merges remain authorized by the person.

## Three rules that always apply

1. **Every worker grills first.** Each worker's first prompt makes it read the task and then run `/grill-me` with the person in its own pane, before any analysis, plan or code. No exceptions per task. See [references/grilling.md](references/grilling.md).
2. **The coordinator always organizes the tasks in waves before spawning anything**, predicting dependency and file overlap, and confirms the plan with the person. Never start all tasks at once without it. Implementation goes only to the wave whose blockers and overlapping tasks are merged. See [references/waves.md](references/waves.md).
3. **Every worker's work is reviewed until a review approves, then automatically creates the PR.** Before `[DONE]`, the worker dispatches a new sub-agent per round to run `/thermo-nuclear-code-quality-review` on its branch diff, fixes the real findings and repeats until a round returns no blocker and no material finding; no fixed round count. Once approved and checks pass, the worker automatically pushes the branch and creates the pull request via `gh pr create`, then reports `[DONE]` with the PR URL and "Review: approved in round N". The coordinator monitors CI and presents it for merge authorization. Tasks tagged `ui: yes` at wave planning also get a front-end review sub-agent each round. See [references/review.md](references/review.md).

## Workflow

1. Read the tasks (issue bodies, dependencies, the code they touch) and plan the waves: [references/waves.md](references/waves.md).
2. Create one worktree and one agent per task: [references/topology.md](references/topology.md).
3. Send each worker its first prompt, grill included: [references/worker-prompts.md](references/worker-prompts.md).
4. Workers report with the tagged protocol, and always check that the coordinator is not on a dialog first: [references/reporting-protocol.md](references/reporting-protocol.md).
5. After the grills, re-check the wave plan against the files each worker expects to touch, then send go messages wave by wave, as the person merges.
6. Workers review their branch until approved: [references/review.md](references/review.md).
7. Handle reports, merges and questions: [references/coordinator-rules.md](references/coordinator-rules.md).
8. When a pull request is merged, clean up proven worktrees: [references/cleanup.md](references/cleanup.md).

## Reference files

| File | Content |
|------|---------|
| [references/waves.md](references/waves.md) | Planning waves, overlap prediction, go messages, re-checking with real diffs |
| [references/grilling.md](references/grilling.md) | The grill every worker starts with |
| [references/topology.md](references/topology.md) | Creating worktrees and agents, names, startup failures |
| [references/worker-prompts.md](references/worker-prompts.md) | Sending prompts, reading workers, first-prompt checklist |
| [references/review.md](references/review.md) | The review loop: new sub-agent per round until approved, and what the coordinator checks |
| [references/review-frontend.md](references/review-frontend.md) | Extra Impeccable review lens, read only for `ui: yes` tasks |
| [references/reporting-protocol.md](references/reporting-protocol.md) | Worker to coordinator messages and tags |
| [references/coordinator-rules.md](references/coordinator-rules.md) | Verification, merging, decisions with the person |
| [references/cleanup.md](references/cleanup.md) | Removing finished worktrees and branches with proof |
