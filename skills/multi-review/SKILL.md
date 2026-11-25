---
name: multi-review
description: "Coordinate several autonomous coding agents (Claude, Antigravity, Kiro, and others) through Herdr to review multiple pull requests in parallel: one isolated read-only worktree and worker per PR, intake and triage by a coordinator, multi-lens diff-review per worker, formal GitHub PR review drafting with inline comments and person confirmation before posting, per-host protocols, and consolidated merge-readiness reporting. Use only when the user asks to review multiple PRs or coordinate parallel PR reviews through Herdr, alongside the herdr and diff-review skills. Do not use for single-session review of one branch or PR diff (use diff-review), implementing issues across Herdr worktrees (use multi-implement), single-issue end-to-end implementation (use implement), or single-agent Herdr pane control (use herdr). Requires HERDR_ENV=1."
---

# Multi-Review

Coordinate a coordinator agent and multiple reviewer worker agents—one PR per worker, each in its own isolated Herdr worktree—to review a queue of pull requests in parallel (requires the companion `herdr` and `diff-review` skills installed alongside it). Load the `herdr` skill first for the CLI itself; this skill is the PR-review coordination workflow on top of it. Detect your host `--kind` from `herdr agent list` (matching `$HERDR_PANE_ID`) and load **only** the matching protocol runbook ([references/protocols/claude.md](references/protocols/claude.md), [references/protocols/agy.md](references/protocols/agy.md), [references/protocols/kiro.md](references/protocols/kiro.md), or [references/protocols/fallback.md](references/protocols/fallback.md) for any other kind).

## Roles

- **Coordinator** (the session that owns the review queue): intakes and triages PRs, assigns `lenses: [<baseline>, ...]` and effort presets, spawns one worktree and worker per PR, monitors progress via `herdr agent wait --until`, and presents a consolidated merge-readiness summary to the person.
- **Reviewer worker** (one PR per worker in v1): checks out its assigned PR in an isolated, strictly read-only worktree, runs multi-lens `diff-review` (single pass, no `grill-me` at startup), drafts a formal GitHub PR review with inline diff comments and verdict (`APPROVE` or `REQUEST_CHANGES`), displays the full review and rationale to the person in its pane, posts to GitHub only after explicit person confirmation, and reports `[DONE <pr>]`.
- **The person** confirms the triaged review queue, validates and confirms each worker's drafted GitHub review before submission, and decides merges.

## Three rules that always apply

1. **Triage and confirm the queue before spawning.** The coordinator intakes the target PRs, prioritizes them, assigns `lenses: [<baseline>, ...]` (`code-quality` for code PRs, `docs-quality` for docs-only PRs, or both for mixed substantial docs), and confirms the queue and effort preset with the person before spawning workers. Workers do **not** run `grill-me` at startup. See [references/intake-and-triage.md](references/intake-and-triage.md).
2. **One PR per worker, strictly read-only.** Each worker inspects one PR in an isolated worktree (`git fetch origin pull/<N>/head`) and never modifies PR code or pushes commits. Fixes belong to the PR author or `multi-implement`. See [references/worker-review.md](references/worker-review.md).
3. **Formal GitHub review is drafted, shown, and person-confirmed.** Workers aggregate findings using `diff-review`'s canonical severities (`blocker`, `material`, `nitpick`, `out-of-scope`): `APPROVE` iff 0 `blocker` and 0 `material`, else `REQUEST_CHANGES`. Before submitting to GitHub, the worker displays the full review summary, inline comments, and rationale to the person in its pane and asks for explicit confirmation via the host's ask protocol. See [references/worker-review.md](references/worker-review.md).

## Workflow

1. Intake and triage the PR queue, assign `lenses: [<baseline>, ...]` and effort preset, and confirm with the person: [references/intake-and-triage.md](references/intake-and-triage.md).
2. Create one isolated worktree and one reviewer worker per PR, choosing the preset from [references/agent-effort.md](references/agent-effort.md) and startup flags from the host protocol: [references/topology.md](references/topology.md).
3. Workers check out the PR read-only, run single-pass multi-lens `diff-review`, draft the formal GitHub review, display it for rationale validation, and post only after person confirmation: [references/worker-review.md](references/worker-review.md).
4. Workers report with the tagged protocol, checking both `agent_status` and `[WAITING-FOR-PERSON]` before prompting, and every wait uses `herdr agent wait --until`: [references/reporting-protocol.md](references/reporting-protocol.md).
5. Handle worker reports, `[TREE]` lens retags, `[QUESTION]` escalations, and present the consolidated multi-PR merge-readiness summary: [references/coordinator-rules.md](references/coordinator-rules.md).
6. Clean up finished PR review worktrees safely once `[DONE <pr>]` is reported: [references/cleanup.md](references/cleanup.md).

## Reference files

| File | Content |
|------|---------|
| [references/intake-and-triage.md](references/intake-and-triage.md) | PR intake, triage/prioritization, `lenses` assignment, and queue confirmation |
| [references/worker-review.md](references/worker-review.md) | Isolated PR checkout, single-pass `diff-review`, canonical severities, formal GitHub review drafting & confirmation |
| [references/coordinator-rules.md](references/coordinator-rules.md) | Worker monitoring, `[TREE]`/`[QUESTION]` handling, consolidated merge-readiness summary |
| [references/topology.md](references/topology.md) | Creating PR worktrees and workers, protocol selection, naming, startup recovery |
| [references/agent-effort.md](references/agent-effort.md) | Model tiers, Presets 1–4 (default Preset 2), and two-tier `diff-review` mapping |
| [references/reporting-protocol.md](references/reporting-protocol.md) | Readiness checks, `[WAITING-FOR-PERSON]`, `herdr agent wait --until`, and tagged messages |
| [references/cleanup.md](references/cleanup.md) | Safely removing finished read-only PR review worktrees |
| [references/protocols/claude.md](references/protocols/claude.md) | `--kind claude` startup flags, `AskUserQuestion`, and `Agent` `diff-review` dispatch |
| [references/protocols/agy.md](references/protocols/agy.md) | `--kind agy` startup flags, `ask_question`, `/tmp` diff artifacts, and `invoke_subagent` dispatch |
| [references/protocols/kiro.md](references/protocols/kiro.md) | `--kind kiro` startup flags, `[WAITING-FOR-PERSON]`, and `subagent` / fallback tab dispatch |
| [references/protocols/fallback.md](references/protocols/fallback.md) | Other `--kind` hosts: bare startup, `[WAITING-FOR-PERSON]`, and temporary Herdr review tabs |
