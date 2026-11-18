# Reporting protocol (workers to the coordinator)

Put this in every worker's prompt, with the coordinator's pane id:

1. **Check the coordinator first (`agent_status` and visible tail).** Run `herdr agent get <coordinator-pane>` to read `agent_status`, and whenever `agent_status` is `idle` or `done`, also inspect `herdr agent read <coordinator-pane> --source visible`:
   - `working`: run `herdr agent wait <coordinator-pane> --until idle --timeout 120000`, then check again from step 1.
   - `blocked` (a blocking dialog is open for the person): **never send a prompt and never press a key.** Run `herdr agent wait <coordinator-pane> --until idle --timeout 120000` and re-check; after three checks while still blocked, stop and tell the person in your own pane instead.
   - `idle` or `done`, **and** the coordinator's latest visible turn ends with `[WAITING-FOR-PERSON]` (match the coordinator's most recent turn in `--source visible`, ignoring trailing TUI input-box/status-bar chrome and ignoring `[WAITING-FOR-PERSON]` from earlier already-answered turns; see [protocols/fallback.md](protocols/fallback.md)): treat the coordinator as blocked on the person — **never send a prompt and never press a key.** Because `agent_status` is already `idle`/`done`, `--until idle` returns immediately; instead wait for the person's reply to start a turn via `herdr agent wait <coordinator-pane> --until working --timeout 120000` (and once `working` is observed, `herdr agent wait <coordinator-pane> --until idle --timeout 120000`), then re-check. After three checks (`3 × 120000` ms) while still waiting on `[WAITING-FOR-PERSON]`, stop and tell the person in your own pane instead.
   - `idle` or `done`, with **no** `[WAITING-FOR-PERSON]` in the latest visible turn: send.
2. Send with `herdr agent prompt <coordinator-pane> "<message>"` (no `--wait`), which natively submits text and Enter. Do not wait for a reply by polling or sleeping; follow the waiting rule below. Never blindly send keys or Enter to the coordinator pane. A stray Enter on a dialog picks its first option, which can accidentally answer the person's question for them.
3. One tagged paragraph per event, no progress chatter:
   - `[DONE <task>]`: finished, committed, pushed, and PR created; PR URL, branch, approved HEAD commit, check result, and a Review paragraph ("Review: approved in round N", with per-lens round counts and findings fixed, rejected, and deferred; see [review.md](review.md)).
   - `[BLOCKED <task>]`: cannot continue, and on what.
   - `[QUESTION <task>]`: a decision that is not the worker's, with options and a recommendation.
   - `[TREE <task>]`: it needs a change to another task, the parent, a dependency link, `lenses: [...]`, or another planning field.
   - `[DONE-READ <task>]` and `[DONE-BODY <task>]`: the read-only step (the grill included, with its decisions and expected files) or a body edit is done.
4. Decisions that need the person go to the person in the worker's own pane, not through the coordinator.

## Waiting between agents (always `herdr agent wait --until`)

Whenever one agent waits on another (worker on coordinator, coordinator on worker, a worker on a pane it started), it uses `herdr agent wait <name> --until <state> --timeout <ms>`. Never `agent prompt --wait`, never `sleep` loops, never repeated `agent get` polling.

1. Send the prompt (without `--wait`), then confirm it started: `herdr agent wait <name> --until working --timeout 15000`. Without this, a still-`idle` target satisfies the next wait instantly.
2. Wait for the outcome (to wait before sending to the coordinator, use `--until idle` alone, as in the check above), naming the states explicitly: `herdr agent wait <name> --until idle --until done --until blocked --timeout <ms>`. Pick `<ms>` for the task (`120000` for a message, longer for a work turn) and repeat the wait on `timeout`; a timeout is not a failure.
3. On `blocked`, do not answer the dialog; inspect with `herdr agent get` and ask the person ([worker-prompts.md](worker-prompts.md)).
