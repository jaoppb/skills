---
name: implement
description: "Implement a single issue, spec, or task end-to-end in one agent session: intake and branch setup, mandatory grill-me interrogation, optional plan-review, implementation with checks and tests, multi-lens diff-review loop via fresh read-only sub-agents until zero blocker and zero material findings, and automated PR creation stopping before merge. Use only when the user explicitly invokes implement or hands over a whole GitHub issue, local spec/plan file, or task to deliver end-to-end as a branch and PR. Do not use for ad-hoc in-session edits, refactors, or \"write this function\" requests, parallel multi-issue orchestration across Herdr worktrees (use herdr-multi-agent), standalone diff/PR reviews without implementing (use diff-review), standalone spec interrogation without implementing (use grill-me), pre-implementation plan/RFC reviews (use plan-review), whole-codebase audits (use codebase-audit), or read-only Q&A and debugging inquiries."
---

# Implement

End-to-end single-session implementation workflow that preserves full engineering discipline — interrogation, tests, checks, multi-lens read-only review, and clean PR handoff — without multi-agent coordination, wave planning, or Herdr (`HERDR_ENV=1`) overhead.

**Companion skills:** Requires `grill-me` and `diff-review` (plus `plan-review` when triggered). Works standalone in any repository and on any host that supports read-only sub-agents.

## Workflow

### 1. Intake & workspace setup

1. **Resolve the task source:**
   - **GitHub issue** (`#N`, URL, or number): fetch the issue body, comments, labels, and linked context (e.g., via `gh issue view`).
   - **Local spec or plan file**: read the target file completely along with any files it references.
   - **Pasted prompt / inline task**: capture the stated goal, constraints, and acceptance criteria from the conversation.
2. **Read project context:** Read repository rules (`AGENTS.md`, `CLAUDE.md`, or equivalent), build/lint/test commands, and the existing code or docs the task touches.
3. **Resume an existing task workspace:** if the current branch or worktree already belongs to this task (named for it, or holding commits that reference it), reuse it instead of re-branching and resume at the first unmet gate: confirmed `grill-me` decisions present → skip §2; task commits present → go to §4 verification and §5. If ownership is ambiguous, ask.
4. **Otherwise, prepare a clean branch off the latest base branch:**
   - Fetch and branch off the latest base branch (e.g., `origin/main` or the repo default) using a clean branch name such as `feat/<slug>` or `fix/<slug>`.
   - **Default:** create and switch to the new branch in the current checkout.
   - **Worktree fallback:** use a `git worktree` only if the user requests it or if the current checkout has unrelated uncommitted/in-progress work (ask before touching or bypassing dirty state; never discard or overwrite someone else's changes).

### 2. Mandatory `grill-me` gate

Run `grill-me` with the user before writing any code to sharpen scope, edge cases, non-goals, and test expectations. Scale the interview to the task (1–3 targeted questions for narrow tasks; deeper interrogation when underspecified).

- **Skip only when:** the target artifact already contains confirmed `grill-me` decisions (`Decisions` / `Non-goals`) that remain current, or the user explicitly waives grilling. Even then, stop and confirm if you uncover an unaddressed contradiction or blocker.
- **Writeback (per `grill-me`):** write confirmed `Decisions`, `Non-goals`, `Open questions`, and `Risks` back in place to the GitHub issue or local spec file before coding, or output them in chat when working from a prompt only.
- **Oversized input:** if grilling (or `plan-review`) shows the task holds multiple independent deliverables, stop and let the user choose: narrow to one slice for this PR (the rest becomes follow-up issues), hand off to `herdr-multi-agent`, or proceed as a single PR on explicit confirmation. Never ship a silent mega-PR.

### 3. Optional `plan-review` gate

Run `plan-review` before implementation **only** if the user requests it or if the task is large, cross-cutting, high-risk (auth, migrations, public contracts, destructive operations), or structurally ambiguous. Otherwise proceed directly to implementation.

### 4. Implement & verify

1. Follow repository rules and existing conventions. Make minimal, surgical changes scoped to the confirmed decisions and non-goals.
2. Add or update tests that verify business intent and edge cases whenever behavior changes.
3. Commit changes cleanly in logical units using the repository's commit style (including issue references such as `Refs #N` when applicable).
4. Run the repository's check, lint, build, and test commands locally until green. Never report checks as passing if anything failed or was skipped.
5. **No automated suite:** if the repository has no runnable checks, run the verification its rules document (e.g., an `AGENTS.md` checklist) plus cheap ad-hoc commands, and state plainly in the PR/handoff that no automated suite exists and what was verified manually. Never claim "checks green".

### 5. Mandatory multi-lens `diff-review` loop

Run `diff-review` against the branch diff (`origin/<base>...HEAD`, or the working-tree/base diff when no remote base exists) **before** opening a PR or declaring done, following its lens selection, dispatch, delta re-run, and escalation rules. Implement-specific seams:

1. **Fail loud without sub-agents:** if the host cannot spawn read-only sub-agents, stop before the PR and report the gap per `diff-review` (no self-review fallback).
2. **Fix in new commits:** address `blocker` and `material` findings in new commits, re-run §4 verification, then run the next `diff-review` delta round until approved.

### 6. PR & handoff

1. **Push and open PR (when GitHub remote and `gh` CLI are available):** unless the user asked to keep changes local, push the branch (`git push -u origin <branch>`) and open the PR (`gh pr create`), including `Closes #N` when implementing a GitHub issue.
   - If there is no GitHub remote/`gh` CLI or the user asked to hold locally, keep the approved commits on the branch and report the branch, HEAD SHA, and diff summary.
2. **Include in the PR body and final handoff:**
   - Concise summary of changes and confirmed scope.
   - Local verification/check results observed after the final commit.
   - `diff-review` summary: approval round, active lenses, and per-lens fixed, rejected (with reason), and deferred (with reason) counts/items.
3. **Stop before merge:** present the PR URL (or local branch) and approved HEAD commit SHA, and wait for the user to authorize merging. **Never merge automatically.**
4. **On request only:** watch CI checks or clean up the finished branch/worktree after merge if the user asks. Post-approval commits (CI fixes, PR feedback) follow `diff-review`'s re-review rule before re-reporting readiness.

## When to use another skill

| Need | Use instead |
| :--- | :--- |
| Multiple tasks/issues in parallel across Herdr worktrees | `herdr-multi-agent` |
| Review an existing diff, branch, or PR without implementing | `diff-review` |
| Interrogate a spec or idea without implementing | `grill-me` |
| Review a drafted plan, epic, or RFC before coding | `plan-review` |
| Audit an entire codebase for debt and improvements | `codebase-audit` |
