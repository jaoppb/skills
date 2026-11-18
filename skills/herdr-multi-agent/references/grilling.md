# Grilling (every worker, always)

Every worker begins with a `grill-me` session with the person in its own pane (invoking the skill and asking questions strictly through its host protocol: [protocols/claude.md](protocols/claude.md), [protocols/agy.md](protocols/agy.md), or [protocols/fallback.md](protocols/fallback.md)), before any analysis, plan or code. This is not optional and not decided per task.

- The coordinator puts the grill in the first prompt of every worker (see [worker-prompts.md](worker-prompts.md)); a worker never skips it because the issue "looks clear".
- Read first, then run the `grill-me` interview on the issue with its comments, the project rules, the product and design documents and the code the task touches, until scope, behaviour, edge cases and tests are sharp. Inside Herdr panes, the host protocol's ask rules strictly override standalone `grill-me`'s open-ended prose fallback: `claude` and `agy` must always use `AskUserQuestion` / `ask_question` (using the UI's free-text **Other** option for open-ended questions, never plain prose), while `fallback.md` hosts end every question turn with `[WAITING-FOR-PERSON]`.
- The grill ends with decisions, not code. The worker writes the sharpened decisions back only into the artifacts it owns, and only after the person confirms in that pane.
- The worker then reports `[DONE-READ <task>]` with the decisions and any file it now expects to touch (the coordinator uses it to re-check the wave plan and `lenses: [...]`, see [waves.md](waves.md)) and waits for the go message.
- Decisions that need the person are asked in the worker's pane, never relayed through the coordinator.
- Many workers grilling at once means many panes waiting on the person. That is expected; the coordinator tells the person which panes are waiting, and does not answer for them.
