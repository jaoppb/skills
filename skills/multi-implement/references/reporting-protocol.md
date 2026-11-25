# Reporting protocol and inter-agent readiness

Put the reporting rules and the coordinator's pane id in every worker's prompt, and apply the same pre-prompt readiness check before prompting **any** Herdr agent pane (`<target>`: coordinator, worker, or fallback reviewer).

1. **Check `<target>` before prompting (`agent_status` and visible tail).** Run `herdr agent get <target>` to read `agent_status`, and whenever `agent_status` is `idle` or `done`, also inspect `herdr agent read <target> --source visible`:
   - `working`: run `herdr agent wait <target> --until idle --until done --timeout 600000` (a work turn), then check again from step 1.
   - `blocked` (a blocking dialog is open for the person): **never send a prompt and never press a key.** A worker waiting on `<coordinator-pane>` runs `herdr agent wait <target> --until idle --until done --timeout 120000` and re-checks (up to three checks, then tells the person in its own pane); a coordinator or worker inspecting a child pane reads the screen and asks the person directly.
   - `idle` or `done`, **and** `<target>`'s latest visible turn ends with `[WAITING-FOR-PERSON]` (match `<target>`'s most recent turn in `--source visible`, ignoring trailing TUI input-box/status-bar chrome and ignoring `[WAITING-FOR-PERSON]` from earlier already-answered turns; see [protocols/kiro.md](protocols/kiro.md) and [protocols/fallback.md](protocols/fallback.md)): treat `<target>` as blocked on the person — **never send a prompt and never press a key.** Because `agent_status` is already `idle`/`done`, waiting for `idle`/`done` returns immediately; a worker waiting on `<coordinator-pane>` waits for the person's reply to start a turn via `herdr agent wait <target> --until working --timeout 120000` (and once `working` is observed, `herdr agent wait <target> --until idle --until done --timeout 120000`), re-checking up to three times (`3 × 120000` ms) before telling the person in its own pane. A coordinator seeing `[WAITING-FOR-PERSON]` on a worker stops and tells the person which pane is waiting.
   - `idle` or `done`, with **no** `[WAITING-FOR-PERSON]` in the latest visible turn: safe to send.
2. Send with `herdr agent prompt <target> "<message>"` (no `--wait`), which natively submits text and Enter. Do not wait for a reply by polling or sleeping; follow the waiting rule below. Never blindly send keys or Enter to an agent pane — a stray Enter on a dialog picks its first option, which can accidentally answer the person's question for them.
3. Worker-to-coordinator messages use one tagged paragraph per event, no progress chatter:
   - `[DONE <task>]`: finished, committed, pushed, and PR created, including the required PR and multi-lens Review summary fields defined in [review.md](review.md).
   - `[BLOCKED <task>]`: cannot continue, and on what.
   - `[QUESTION <task>]`: a decision that is not the worker's, with options and a recommendation.
   - `[TREE <task>]`: it needs a change to another task, the parent, a dependency link, `lenses: [...]`, or another planning field.
   - `[DONE-READ <task>]` and `[DONE-BODY <task>]`: the read-only step (the grill included, with its decisions and expected files) or a body edit is done.
4. Decisions that need the person go to the person in the worker's own pane, not through the coordinator.

## Waiting between agents (always `herdr agent wait --until`)

Whenever one agent waits on another (worker on coordinator, coordinator on worker, a worker on a pane it started), it uses `herdr agent wait <name> --until <state> --timeout <ms>`. Never `agent prompt --wait`, never `sleep` loops, never repeated `agent get` polling.

1. Send the prompt (without `--wait`), then confirm it started: `herdr agent wait <name> --until working --timeout 15000`. Without this, a still-`idle`/`done` target satisfies the next wait instantly.
2. Wait for the outcome, naming the states explicitly: `herdr agent wait <name> --until idle --until done --until blocked --timeout <ms>`. Use `120000` for a message round-trip and `600000` for a work turn (implementation, review round), and repeat the wait on `timeout`; a timeout is not a failure, and each re-issued wait costs the waiting agent a turn.
3. When the wait finishes, check `<name>` with step 1 above (`agent_status` plus `--source visible` for `[WAITING-FOR-PERSON]`), and read its output with `--source recent-unwrapped --lines 40` rather than the whole screen ([worker-prompts.md](worker-prompts.md#reading-a-worker)). If `blocked` or ending in `[WAITING-FOR-PERSON]`, never answer or overwrite the question; inspect and surface it to the person ([worker-prompts.md](worker-prompts.md)).
