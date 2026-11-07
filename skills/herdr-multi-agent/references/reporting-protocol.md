# Reporting protocol (workers to the coordinator)

Put this in every worker's prompt, with the coordinator's pane id:

1. **Check the coordinator first.** Run `herdr agent get <coordinator-pane>` and read `agent_status`.
   - `idle` or `done`: send.
   - `working`: `herdr agent wait <coordinator-pane> --until idle --timeout 120000`, then check again. Wait only for `idle`: that is the state in which the worker can send.
   - `blocked` (a question dialog is open for the person): never send and never press a key to it. Check again, and after three checks tell the person in your own pane instead.
2. Send with `herdr agent prompt <coordinator-pane> "<message>"` (no `--wait`), which natively submits text and Enter. Do not wait for a reply by polling or sleeping; follow the waiting rule below. Never blindly send keys or Enter to the coordinator pane. A stray Enter on a dialog picks its first option, which can accidentally answer the person's question for them.
3. One tagged paragraph per event, no progress chatter:
   - `[DONE <task>]`: finished, committed, pushed, and PR created; PR URL, branch, approved HEAD commit, check result, and a Review paragraph ("Review: approved in round N", findings fixed, rejected and deferred per round; see [review.md](review.md)).
   - `[BLOCKED <task>]`: cannot continue, and on what.
   - `[QUESTION <task>]`: a decision that is not the worker's, with options and a recommendation.
   - `[TREE <task>]`: it needs a change to another task, the parent, a dependency link or a planning field.
   - `[DONE-READ <task>]` and `[DONE-BODY <task>]`: the read-only step (the grill included, with its decisions and expected files) or a body edit is done.
4. Decisions that need the person go to the person in the worker's own pane, not through the coordinator.

## Waiting between agents (always `herdr agent wait --until`)

Whenever one agent waits on another (worker on coordinator, coordinator on worker, a worker on a pane it started), it uses `herdr agent wait <name> --until <state> --timeout <ms>`. Never `agent prompt --wait`, never `sleep` loops, never repeated `agent get` polling.

1. Send the prompt (without `--wait`), then confirm it started: `herdr agent wait <name> --until working --timeout 15000`. Without this, a still-`idle` target satisfies the next wait instantly.
2. Wait for the outcome (to wait before sending to the coordinator, use `--until idle` alone, as in the check above), naming the states explicitly: `herdr agent wait <name> --until idle --until done --until blocked --timeout <ms>`. Pick `<ms>` for the task (`120000` for a message, longer for a work turn) and repeat the wait on `timeout`; a timeout is not a failure.
3. On `blocked`, do not answer the dialog; inspect with `herdr agent get` and ask the person ([worker-prompts.md](worker-prompts.md)).
