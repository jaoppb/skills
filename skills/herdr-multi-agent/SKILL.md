---
name: herdr-multi-agent
description: "Coordinate several autonomous coding agents (Claude, Antigravity, Kiro, and others) through Herdr: one worktree and one agent per task, every agent starting with a grill-me session, a coordinator that always models tasks as a dependency graph with multi-lens diff-review tags (and optional pre-run plan-review), read-only review until approved before any merge, per-host protocols, and a tagged reporting protocol. Use only when the user asks to start, organize or coordinate multiple agents or worktrees with Herdr, alongside the herdr skill. Do not use for single-agent Herdr pane control (use herdr) or sub-agent delegation outside Herdr. Requires HERDR_ENV=1."
---

# Herdr multi-agent coordination

Lessons from running a coordinator agent and several worker agents, one per task, each in its own Herdr worktree (requires the companion `herdr`, `grill-me`, `diff-review`, and `plan-review` skills installed alongside it). Load the `herdr` skill first for the CLI itself; this skill is the working method on top of it. Detect your host `--kind` from `herdr agent list` (matching `$HERDR_PANE_ID`) and load **only** the matching protocol runbook ([references/protocols/claude.md](references/protocols/claude.md), [references/protocols/agy.md](references/protocols/agy.md), [references/protocols/kiro.md](references/protocols/kiro.md), or [references/protocols/fallback.md](references/protocols/fallback.md) for any other kind). The workflow details live in the reference files linked below; read the one that matches the step you are on.

## Roles

- **Coordinator** (the session that owns the whole effort): owns the task tree, shared documents, the dependency graph and the people-facing decisions. It does not implement the workers' tasks.
- **Worker** (one per task): owns one task and only the artifacts of that task (for example its own issue body or its own branch). It never edits the coordinator's artifacts, another worker's artifacts, the parent, dependency links or planning fields; it asks the coordinator.
- **The person** decides merges, permissions, and major scope changes. Pull request creation is automated once a worker's review approves. Workers rebase, push, and open PRs automatically; merges remain authorized by the person.

## Three rules that always apply

1. **Every worker grills first.** Each worker's first prompt makes it read the task and then run `grill-me` with the person in its own pane (using its host protocol's skill and ask mechanics), before any analysis, plan or code. No exceptions per task. See [references/grilling.md](references/grilling.md).
2. **The coordinator always builds the task dependency graph before spawning anything**, mapping declared dependencies, predicted file-overlap edges, and `lenses: [<baseline>, ...]` (`code-quality` for code tasks, `docs-quality` for docs-only tasks, or both for mixed substantial docs), optionally running `plan-review` when requested or when the breakdown looks under-refined/high-risk, and confirms the graph with the person. Never start all tasks at once without it. Spawn a worker only once all of its blockers (declared dependencies and overlap predecessors) are merged (to avoid prompt-cache expiry and full-context re-reads while idle). See [references/dependency-graph.md](references/dependency-graph.md).
3. **Every worker's work is reviewed until a review approves, then automatically creates the PR.** Before `[DONE]`, the worker runs multi-lens `diff-review` (its content-aware baseline plus assigned specialist lenses) via fresh read-only reviewers round by round until every active lens returns zero blocker and zero material findings; it then pushes and opens the PR, and the coordinator monitors CI and presents it for merge authorization. See [references/review.md](references/review.md).

## Workflow

1. Read the tasks (issue bodies, dependencies, the code/docs they touch), build the dependency graph and assign `lenses: [<baseline>, ...]`, and optionally run `plan-review` on under-refined/high-risk breakdowns before graph confirmation: [references/dependency-graph.md](references/dependency-graph.md).
2. For tasks whose blockers are all merged (initially only root tasks), create one worktree and one agent per task, choosing the preset from [references/agent-effort.md](references/agent-effort.md) and startup flags from the host protocol: [references/topology.md](references/topology.md).
3. Send each spawned worker its first prompt, grill and host protocol included: [references/worker-prompts.md](references/worker-prompts.md).
4. Workers report with the tagged protocol, always check both `agent_status` and the `[WAITING-FOR-PERSON]` visible tail so they never interrupt an open question, and every wait between agents uses `herdr agent wait --until`: [references/reporting-protocol.md](references/reporting-protocol.md).
5. As each spawned worker finishes its grill (`[DONE-READ]`), re-check graph overlap and `lenses` against the files it expects to touch, and send `go` promptly (holding idle only if a newly discovered overlap hits a still-running task).
6. Workers run multi-lens `diff-review` on their branch until approved: [references/review.md](references/review.md).
7. Handle reports, merges and questions: [references/coordinator-rules.md](references/coordinator-rules.md).
8. When a pull request is merged, clean up proven worktrees and spawn newly unblocked tasks: [references/cleanup.md](references/cleanup.md).

## Reference files

| File | Content |
|------|---------|
| [references/protocols/claude.md](references/protocols/claude.md) | `--kind claude` startup flags, `/grill-me`, `/diff-review`, & `/plan-review`, blocking `AskUserQuestion`, and `Agent` review dispatch |
| [references/protocols/agy.md](references/protocols/agy.md) | `--kind agy` startup flags, `SKILL.md` loading, blocking `ask_question`, `/tmp` artifact prep, and `invoke_subagent` review dispatch |
| [references/protocols/kiro.md](references/protocols/kiro.md) | `--kind kiro` preflight `~/.kiro/agents/` sync, `chat` + `--agent`/`--model`/`--effort` startup flags, `[WAITING-FOR-PERSON]` sentinel, and `subagent` review dispatch |
| [references/protocols/fallback.md](references/protocols/fallback.md) | All other `--kind` agents: bare startup, `[WAITING-FOR-PERSON]` sentinel, and temporary Herdr review-tab dispatch |
| [scripts/sync_kiro_agents.py](scripts/sync_kiro_agents.py) | Idempotent `~/.kiro/agents/` sync and `--check` preflight rendering `herdr-*`, read-only `diff-review-*`, and read-only `plan-review-*` profiles from [references/kiro-agents/](references/kiro-agents/) |
| [references/dependency-graph.md](references/dependency-graph.md) | Building the dependency graph, overlap prediction, `lenses: [<baseline>, ...]`, optional pre-run `plan-review`, spawning unblocked tasks on merge, dispatching `go` after `[DONE-READ]`, re-checking with real diffs |
| [references/grilling.md](references/grilling.md) | The grill every worker starts with |
| [references/agent-effort.md](references/agent-effort.md) | Model tiers and selectable presets (Presets 1–4, default Preset 2; Top is opt-in) for coordinators and workers |
| [references/topology.md](references/topology.md) | Creating worktrees and agents, protocol selection, names, startup failures |
| [references/worker-prompts.md](references/worker-prompts.md) | Sending prompts, reading workers, first-prompt checklist |
| [references/review.md](references/review.md) | Multi-lens `diff-review` worker loop (with smart delta re-runs) and optional coordinator pre-run `plan-review` |
| [references/reporting-protocol.md](references/reporting-protocol.md) | Worker to coordinator messages, `[WAITING-FOR-PERSON]` visible-tail check, and tags |
| [references/coordinator-rules.md](references/coordinator-rules.md) | Verification, merging, decisions with the person |
| [references/cleanup.md](references/cleanup.md) | Removing finished worktrees and branches with proof |
