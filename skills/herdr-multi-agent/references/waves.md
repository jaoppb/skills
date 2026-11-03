# Waves

The coordinator always plans waves before it spawns agents or sends any go message. Never start every task at once and hope the branches do not collide.

## Planning the waves (before spawning)

1. List the tasks and read each issue body, its dependencies and the code areas it names (screens, wiring traits, error enums, design docs, the shared plan, migrations).
2. Predict the **file overlap**: two tasks that touch the same module, screen or document cannot be in the same implementation wave. Use the issue text, `docs/design/` and a quick search of the code to find the likely files. When unsure, treat tasks of the same area as overlapping.
3. Assign waves: dependency order first (a blocked task is in a later wave), then overlap (of two overlapping tasks, the one on the critical path or with more dependents goes first). Tasks with no dependency and no overlap share a wave.
4. Show the wave plan to the person (tasks per wave, why each split) and get it confirmed before the first go message.

## Running the waves

- Every worker starts with the grill (see [grilling.md](grilling.md)), whatever its wave, because grilling is read-only. After the grill the worker waits for a go message.
- Send the go message to wave N only after the person has merged wave N-1 (or, for tasks with no overlap, after the plan says they may run together). The worker then rebases again and implements.
- A task whose blocker is not merged does not write code. Give it the read-only step (rebase, compare the plan with the code, report mismatches) and tell it to wait for the go message.
- A task that needs a written artifact before its code (a canvas, a design) waits for it: do not let a worker implement first.
- **Re-check the overlap with real diffs.** The grill and the code can reveal files the prediction missed. Before two branches both go to review, compare their changed files (`git diff --name-only <base>..HEAD` on each, then `comm -12` of the sorted lists). When they share files, choose the merge order, tell the other worker to hold its push, and send it a go message to rebase and resolve the conflicts (keep both sides' intent, then sync the shared plan) once the first is merged. Move the task to a later wave in the plan and tell the person.
- Move planning cards by hand when the automatic sync would also move something that was held on purpose.
