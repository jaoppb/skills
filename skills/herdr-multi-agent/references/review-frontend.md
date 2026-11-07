# Front-end review lens (Impeccable)

Read this only when the task is tagged `ui: yes`. Back-end tasks never load it. It adds a second reviewer to each round of [review.md](review.md); it does not replace the code-quality review.

## The round

1. In every round, dispatch the code-quality sub-agent from [review.md](review.md) **and** a separate fresh sub-agent for this lens, on the same diff (`git diff origin/<base>..HEAD`). Never reuse either, and never fold the two lenses into one sub-agent.
2. The front-end sub-agent runs the project's Impeccable `audit` on the UI-bearing parts of the diff and **reports only; it edits nothing**. Give it the earlier rounds' findings (fixed, rejected, deferred) for this lens, so it looks for what is new.
3. Impeccable is the project's installed skill: a project-local variant (for example a modified non-web one) wins over the upstream [`pbakaus/impeccable`](https://github.com/pbakaus/impeccable). Do not vendor or copy it.
4. Map the `audit` severities to the loop: **P0 = blocker, P1 = material**, P2/P3 = nitpicks the worker may reject with a reason. The round approves this lens when it returns no P0 and no P1. The whole round approves only when both lenses do.
5. `critique` (the scored UX review) is not part of the loop; it stays with the person at PR review.

## When Impeccable is not usable

If no Impeccable skill is available in the project, or it was never initialised (no `PRODUCT.md`), do not skip the lens. Send `[BLOCKED <task>]` naming what is missing. The coordinator asks the person to install it (`pbakaus/impeccable`, or the project's variant) or to waive the lens for this task. A waiver is recorded in the `[DONE]` Review paragraph.

## The report

For a `ui: yes` task the `[DONE]` Review paragraph states both lenses: rounds, and findings fixed, rejected and deferred for each (or "front-end lens waived by the person").

## Conflicts between lenses

When the two lenses ask for opposite changes, the worker does not pick a winner silently: it sends `[QUESTION <task>]` with both findings and a recommendation.
