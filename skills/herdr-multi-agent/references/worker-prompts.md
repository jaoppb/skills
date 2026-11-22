# Prompts to and reads of a worker

## Sending a prompt

1. Say what to do first (for example `git fetch origin && git rebase origin/main`), then the scope, then where to stop. Workers automatically push and create the pull request once their review approves, then stop for merge.
2. Check `<name>` is ready first ([reporting-protocol.md](reporting-protocol.md)), then send `herdr agent prompt <name> "<text>"`, which natively submits text and Enter. Check with `herdr agent get <name>` that the agent transitioned to `working`. Only send `herdr agent send-keys <name> enter` if inspection shows the prompt text remained pasted but unsubmitted in the pane (and ensure `<name>` is neither `blocked` on a dialog nor waiting at `[WAITING-FOR-PERSON]`).
3. Do not use `agent prompt --wait`. After sending, wait with `herdr agent wait <name> --until ... --timeout <ms>` as in [reporting-protocol.md](reporting-protocol.md#waiting-between-agents-always-herdr-agent-wait---until), and never on yourself.
4. Never send a prompt or keys to an agent that is `blocked` on a dialog or whose latest visible turn ends with `[WAITING-FOR-PERSON]` ([reporting-protocol.md](reporting-protocol.md)): read its screen and tell the person which pane is waiting.

## Reading a worker

- Read a short tail, not the whole screen. When the agent is idle or done, use `herdr agent read <name> --source recent-unwrapped --lines 40`. While it is `working`, `agent read --lines N` fails (`agent_not_idle`), so use `--source visible` only then and for the `[WAITING-FOR-PERSON]` check ([reporting-protocol.md](reporting-protocol.md)).
- Compaction can happen while a worker is idle; its context survives in a summary, so restate the essentials in the next prompt.

## First prompt of a worker (checklist)

- The task id and where its plan lives.
- The worker's host protocol file ([protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), [protocols/kiro.md](protocols/kiro.md), or [protocols/fallback.md](protocols/fallback.md)) so the worker loads only its own host's skill, ask/sentinel, and review-dispatch mechanics.
- The exact reference files the worker reads: its protocol file, [grilling.md](grilling.md), [reporting-protocol.md](reporting-protocol.md), and [review.md](review.md) (unless review is waived). Tell it not to read the rest of the skill tree.
- First command (rebase), then **the grill**: read the issue, rules and code, then run `grill-me` with the person in this pane ([grilling.md](grilling.md)) using the worker's protocol file. No implementation until the go message.
- Scope: which operations of the plan are its own, and which are another task's.
- Currently running concurrent tasks (and their predicted files) plus merged predecessors whose code or decisions it builds on, noting that it waits after `[DONE-READ]` only for the coordinator's overlap/`lenses` check and `go`.
- Commit message format and the parent reference that does not close the parent.
- A long brief (more than a few paragraphs, or with quotes) goes in a file: keep it to about 40 lines or fewer, link the issue and docs instead of pasting their contents, write it under `/tmp`, then send `herdr agent prompt <name> "Read <file> completely and follow it."`. A long inline prompt can arrive empty, and `>/dev/null` hides the failure; confirm with `herdr agent get <name>` that it went to `working`.
- The review and PR creation: the worker follows [review.md](review.md) and the installed `diff-review` skill ([diff-review/SKILL.md](../../diff-review/SKILL.md)) — one fresh read-only reviewer per active lens per round with smart delta re-runs until approved, then push, `gh pr create`, and report `[DONE <task>]` in the format specified by [review.md](review.md). Merging remains authorized by the person.
- The task's review lenses (`lenses: [<baseline>, ...]`): always list the task's mandatory baseline(s) (`code-quality` for code tasks, `docs-quality` for docs-only tasks, or both for mixed substantial docs) explicitly alongside all assigned specialist lenses; if the worker's diff triggers an unassigned lens from `diff-review` or discovered external specialists, the worker sends `[TREE <task>]` and waits for coordinator retag + overlap check before running/finishing review (never self-retag).
- The reporting protocol with both the `agent_status` check and the `[WAITING-FOR-PERSON]` visible-tail check, plus the coordinator's pane id ([reporting-protocol.md](reporting-protocol.md)).
- What it must not edit.
