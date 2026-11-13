# Prompts to and reads of a worker

## Sending a prompt

1. Say what to do first (for example `git fetch origin && git rebase origin/main`), then the scope, then where to stop. Workers automatically push and create the pull request once their review approves, then stop for merge.
2. `herdr agent prompt <name> "<text>"` natively submits text and Enter. Check with `herdr agent get <name>` that the agent transitioned to `working`. Only send `herdr agent send-keys <name> enter` if inspection shows the prompt text remained pasted but unsubmitted in the pane (and ensure the agent is not `blocked` on a dialog before sending keys).
3. Do not use `agent prompt --wait`. After sending, wait with `herdr agent wait <name> --until ... --timeout <ms>` as in [reporting-protocol.md](reporting-protocol.md#waiting-between-agents-always-herdr-agent-wait---until), and never on yourself.
4. Do not send a prompt to an agent that is `blocked` on a dialog: read its screen and ask the person first.

## Reading a worker

- While an agent is `working`, `agent read --lines N` fails (`agent_not_idle`); use `--source visible`. When it is idle or done, `--source recent-unwrapped` works.
- Compaction can happen while a worker is idle; its context survives in a summary, so restate the essentials in the next prompt.

## First prompt of a worker (checklist)

- The task id and where its plan lives.
- First command (rebase), then **the grill**: read the issue, rules and code, then run `/grill-me` (or conduct the equivalent grilling interview directly if `/grill-me` is not registered) with the person in this pane ([grilling.md](grilling.md)). No implementation until the go message.
- Scope: which operations of the plan are its own, and which are another task's.
- Its wave and what it waits for.
- Commit message format and the parent reference that does not close the parent.
- A long brief (more than a few paragraphs, or with quotes) goes in a file: write it under `/tmp`, then send `herdr agent prompt <name> "Read <file> completely and follow it."`. A long inline prompt can arrive empty, and `>/dev/null` hides the failure; confirm with `herdr agent get <name>` that it went to `working`.
- The review and PR creation: the worker follows [review.md](review.md) (a fresh sub-agent per round until approved, then push and `gh pr create`); `[DONE]` carries the PR URL, "Review: approved in round N" and the approved HEAD. Merging remains authorized by the person.
- The task's tag: `ui: yes` adds "each review round also runs the front-end lens, read `references/review-frontend.md` of the `herdr-multi-agent` skill"; `ui: no` adds only "if your diff touches UI files, send `[TREE]` asking for a retag". Never put front-end review text in a `ui: no` prompt.
- The reporting protocol with the state check and the coordinator's pane id ([reporting-protocol.md](reporting-protocol.md)).
- What it must not edit.
