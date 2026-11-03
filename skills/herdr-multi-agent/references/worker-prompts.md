# Prompts to and reads of a worker

## Sending a prompt

1. Say what to do first (for example `git fetch origin && git rebase origin/main`), then the scope, then where to stop. Workers automatically push and create the pull request once their review approves, then stop for merge.
2. `herdr agent prompt <name> "<text>"` can leave the text pasted but unsubmitted. After it, run `herdr agent send-keys <name> enter`, wait a few seconds and confirm with `herdr agent get <name>` that it went to `working`.
3. Do not use `--wait` when the target is yourself or when you do not want to block.
4. Do not send a prompt to an agent that is `blocked` on a dialog: read its screen and ask the person first.

## Reading a worker

- While an agent is `working`, `agent read --lines N` fails (`agent_not_idle`); use `--source visible`. When it is idle or done, `--source recent-unwrapped` works.
- Compaction can happen while a worker is idle; its context survives in a summary, so restate the essentials in the next prompt.

## First prompt of a worker (checklist)

- The task id and where its plan lives.
- First command (rebase), then **the grill**: read the issue, rules and code, then run `/grill-me` with the person in this pane ([grilling.md](grilling.md)). No implementation until the go message.
- Scope: which operations of the plan are its own, and which are another task's.
- Its wave and what it waits for.
- Commit message format and the parent reference that does not close the parent.
- A long brief (more than a few paragraphs, or with quotes) goes in a file: write it under `/tmp`, then send `herdr agent prompt <name> "Read <file> completely and follow it."` and `send-keys enter`. A long inline prompt can arrive empty, and `>/dev/null` hides the failure; confirm with `herdr agent get <name>` that it went to `working`.
- The review and PR creation: the worker dispatches a new sub-agent per round to run `/thermo-nuclear-code-quality-review` on its branch diff, fixes the real findings and repeats until a round approves (no blocker and no material finding), with no fixed round count. Once approved and checks pass, the worker automatically pushes the branch and creates the pull request (`gh pr create`). `[DONE]` reports the PR URL, "Review: approved in round N", and the approved HEAD. Merging remains authorized by the person.
- The reporting protocol with the state check and the coordinator's pane id ([reporting-protocol.md](reporting-protocol.md)).
- What it must not edit.
