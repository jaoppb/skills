# Reporting protocol (workers to the coordinator)

Put this in every worker's prompt, with the coordinator's pane id:

1. **Check the coordinator first.** Run `herdr agent get <coordinator-pane>` and read `agent_status`.
   - `idle` or `done`: send.
   - `working`: `herdr agent wait <coordinator-pane> --timeout 120000`, then check again.
   - `blocked` (a question dialog is open for the person): never send and never press a key to it. Check again, and after three checks tell the person in your own pane instead.
2. Send with `herdr agent prompt <coordinator-pane> "<message>"` (no `--wait`), then `herdr agent send-keys <coordinator-pane> enter`. Never send keys to the coordinator for any other purpose. A stray enter on a dialog picks its first option, which can answer the person's question for them.
3. One tagged paragraph per event, no progress chatter:
   - `[DONE <task>]`: finished, committed, pushed, and PR created; PR URL, branch, approved HEAD commit, check result, and a Review paragraph ("Review: approved in round N", findings fixed, rejected and deferred per round; see [review.md](review.md)).
   - `[BLOCKED <task>]`: cannot continue, and on what.
   - `[QUESTION <task>]`: a decision that is not the worker's, with options and a recommendation.
   - `[TREE <task>]`: it needs a change to another task, the parent, a dependency link or a planning field.
   - `[DONE-READ <task>]` and `[DONE-BODY <task>]`: the read-only step (the grill included, with its decisions and expected files) or a body edit is done.
4. Decisions that need the person go to the person in the worker's own pane, not through the coordinator.
