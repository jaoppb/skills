# Grilling (every worker, always)

Every worker begins with a `/grill-me` session with the person, in its own pane, before any analysis, plan or code. This is not optional and not decided per task.

- The coordinator puts the grill in the first prompt of every worker (see [worker-prompts.md](worker-prompts.md)); a worker never skips it because the issue "looks clear".
- Read first, then grill: the issue with its comments, the project rules, the product and design documents and the code the task touches. Questions are one at a time, hard, each with a recommended answer, until scope, behaviour, edge cases and tests are sharp.
- The grill ends with decisions, not code. The worker writes the sharpened decisions back only into the artifacts it owns, and only after the person confirms in that pane.
- The worker then reports `[DONE-READ <task>]` with the decisions and any file it now expects to touch (the coordinator uses it to re-check the wave plan, see [waves.md](waves.md)) and waits for the go message.
- Decisions that need the person are asked in the worker's pane, never relayed through the coordinator.
- Many workers grilling at once means many panes waiting on the person. That is expected; the coordinator tells the person which panes are waiting, and does not answer for them.
