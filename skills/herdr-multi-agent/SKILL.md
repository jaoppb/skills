---
name: herdr-multi-agent
description: "Coordinate several autonomous coding agents (Claude, Antigravity, and others) through Herdr: one worktree and one agent per task, every agent starting with a grill-me session, a coordinator that always plans tasks in waves with multi-lens code-review tags, read-only review until approved before any merge, per-host protocols, and a tagged reporting protocol. Use only when the user asks to start, organize or coordinate multiple agents or worktrees with Herdr, alongside the herdr skill. Do not use for single-agent Herdr pane control (use herdr) or sub-agent delegation outside Herdr. Requires HERDR_ENV=1."
---

# Herdr multi-agent coordination

Lessons from running a coordinator agent and several worker agents, one per task, each in its own Herdr worktree. Load the `herdr` skill first for the CLI itself; this skill is the working method on top of it. Detect your host `--kind` from `herdr agent list` (matching `$HERDR_PANE_ID`) and load **only** the matching protocol runbook ([references/protocols/claude.md](references/protocols/claude.md), [references/protocols/agy.md](references/protocols/agy.md), or [references/protocols/fallback.md](references/protocols/fallback.md) for any other kind). The workflow details live in the reference files linked below; read the one that matches the step you are on.

## Roles

- **Coordinator** (the session that owns the whole effort): owns the task tree, shared documents, dependency order, the wave plan and the people-facing decisions. It does not implement the workers' tasks.
- **Worker** (one per task): owns one task and only the artifacts of that task (for example its own issue body or its own branch). It never edits the coordinator's artifacts, another worker's artifacts, the parent, dependency links or planning fields; it asks the coordinator.
- **The person** decides merges, permissions, and major scope changes. Pull request creation is automated once a worker's review approves. Workers rebase, push, and open PRs automatically; merges remain authorized by the person.

## Three rules that always apply

1. **Every worker grills first.** Each worker's first prompt makes it read the task and then run `grill-me` with the person in its own pane (using its host protocol's skill and ask mechanics), before any analysis, plan or code. No exceptions per task. See [references/grilling.md](references/grilling.md).
2. **The coordinator always organizes the tasks in waves before spawning anything**, predicting dependency, file overlap, and `lenses: [code-quality, ...]`, and confirms the plan with the person. Never start all tasks at once without it. Implementation goes only to the wave whose blockers and overlapping tasks are merged. See [references/waves.md](references/waves.md).
3. **Every worker's work is reviewed until a review approves, then automatically creates the PR.** Before `[DONE]`, the worker runs multi-lens `code-review` (`code-quality` baseline plus assigned specialist lenses) via fresh read-only reviewers round by round until every active lens returns zero blocker and zero material findings; it then pushes and opens the PR, and the coordinator monitors CI and presents it for merge authorization. See [references/review.md](references/review.md).

## Workflow

1. Read the tasks (issue bodies, dependencies, the code they touch) and plan the waves and `lenses: [code-quality, ...]`: [references/waves.md](references/waves.md).
2. Create one worktree and one agent per task, choosing the preset from [references/agent-effort.md](references/agent-effort.md) and startup flags from the host protocol: [references/topology.md](references/topology.md).
3. Send each worker its first prompt, grill and host protocol included: [references/worker-prompts.md](references/worker-prompts.md).
4. Workers report with the tagged protocol, always check both `agent_status` and the `[WAITING-FOR-PERSON]` visible tail so they never interrupt an open question, and every wait between agents uses `herdr agent wait --until`: [references/reporting-protocol.md](references/reporting-protocol.md).
5. After the grills, re-check the wave plan and `lenses` against the files each worker expects to touch, then send go messages wave by wave, as the person merges.
6. Workers run multi-lens `code-review` on their branch until approved: [references/review.md](references/review.md).
7. Handle reports, merges and questions: [references/coordinator-rules.md](references/coordinator-rules.md).
8. When a pull request is merged, clean up proven worktrees: [references/cleanup.md](references/cleanup.md).

## Reference files

| File | Content |
|------|---------|
| [references/protocols/claude.md](references/protocols/claude.md) | `--kind claude` startup flags, `/grill-me` & `/code-review`, blocking `AskUserQuestion`, and `Agent` review dispatch |
| [references/protocols/agy.md](references/protocols/agy.md) | `--kind agy` startup flags, `SKILL.md` loading, blocking `ask_question`, `/tmp` diff prep, and `invoke_subagent` review dispatch |
| [references/protocols/fallback.md](references/protocols/fallback.md) | All other `--kind` agents: bare startup, `[WAITING-FOR-PERSON]` sentinel, and temporary Herdr review-tab dispatch |
| [references/waves.md](references/waves.md) | Planning waves, overlap prediction, `lenses: [code-quality, ...]`, go messages, re-checking with real diffs |
| [references/grilling.md](references/grilling.md) | The grill every worker starts with |
| [references/agent-effort.md](references/agent-effort.md) | Model tiers and selectable presets (Presets 1–4) for coordinators and workers |
| [references/topology.md](references/topology.md) | Creating worktrees and agents, protocol selection, names, startup failures |
| [references/worker-prompts.md](references/worker-prompts.md) | Sending prompts, reading workers, first-prompt checklist |
| [references/review.md](references/review.md) | Multi-lens `code-review` loop with smart delta re-runs until approved, and what the coordinator checks |
| [references/reporting-protocol.md](references/reporting-protocol.md) | Worker to coordinator messages, `[WAITING-FOR-PERSON]` visible-tail check, and tags |
| [references/coordinator-rules.md](references/coordinator-rules.md) | Verification, merging, decisions with the person |
| [references/cleanup.md](references/cleanup.md) | Removing finished worktrees and branches with proof |
