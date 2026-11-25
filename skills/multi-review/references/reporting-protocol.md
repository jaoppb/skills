# Reporting protocol and inter-agent readiness

Include these reporting rules and the coordinator's pane ID in every worker's first prompt, and run the same pre-prompt readiness check before prompting **any** Herdr agent pane (`<target>`).

1. **Check `<target>` before prompting (`agent_status` and visible tail).** Run `herdr agent get <target>`, and whenever `agent_status` is `idle` or `done`, also inspect `herdr agent read <target> --source visible`:
   - `working`: run `herdr agent wait <target> --until idle --until done --until blocked --timeout 600000`, then re-check from step 1.
   - `blocked` (a blocking dialog is open for the person): **never send a prompt and never press a key.** A worker waiting on `<coordinator-pane>` waits with `herdr agent wait <target> --until idle --until done --timeout 120000` (up to three checks, then tells the person in its own pane); a coordinator inspecting a worker pane reads the screen and surfaces it to the person.
   - `idle` or `done`, **and** `<target>`'s latest visible turn ends with `[WAITING-FOR-PERSON]` (ignoring trailing TUI input/status chrome and earlier already-answered turns; see [protocols/kiro.md](protocols/kiro.md) and [protocols/fallback.md](protocols/fallback.md)): treat `<target>` as blocked on the person — **never send a prompt and never press a key.** Wait via `herdr agent wait <target> --until working --timeout 120000` (then `--until idle --until done --timeout 120000`), or if coordinator, tell the person which pane is waiting.
   - `idle` or `done`, with **no** `[WAITING-FOR-PERSON]` in the latest visible turn: safe to send.
2. **Send without `--wait`**: Run `herdr agent prompt <target> "<message>"`. Never blindly send keys or Enter to an agent pane.
3. **Worker-to-coordinator tags** (one tagged paragraph per event, no progress chatter):
   - `[DONE <pr>]`: review finished (and formal GitHub review posted or declined by person), including PR URL, reviewed HEAD SHA, active `lenses`, verdict (`APPROVE` / `REQUEST_CHANGES`), finding counts, and GitHub review URL/status.
   - `[BLOCKED <pr>]`: cannot continue, and on what.
   - `[QUESTION <pr>]`: a decision outside the worker's scope, with options and a recommendation.
   - `[TREE <pr>]`: diff triggers an unassigned `diff-review` lens; lists the lens(es) and files and waits for `go`.
4. **Person-facing review confirmation stays in the worker's pane**: Displaying the drafted GitHub review/inline comments and asking the person to confirm posting happens directly in the worker's pane, never relayed through the coordinator.

## Waiting between agents (`herdr agent wait --until`)

Whenever one agent waits on another, use `herdr agent wait <name> --until <state> --timeout <ms>` (never `agent prompt --wait` or `sleep` loops):

1. After `herdr agent prompt <name> ...`, confirm turn start: `herdr agent wait <name> --until working --timeout 15000`.
2. Wait for completion: `herdr agent wait <name> --until idle --until done --until blocked --timeout <ms>` (`120000` for a message round-trip, `600000` for a review turn; repeat on `timeout`).
3. Re-check readiness (`agent_status` + `--source visible`) and read output via `herdr agent read <name> --source recent-unwrapped --lines 40`.
