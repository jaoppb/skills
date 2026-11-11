# Open decisions

The code can't answer these. Ask each one on its own and put the recommended option first. When the repository or its rules doc already settles a decision, say so and use that answer.

## D1. Where does a piece of work live?

| Option | Meaning | Recommend when |
|--------|---------|----------------|
| **Issue mode** | Every SPDD run belongs to a GitHub issue, read and written with `gh`. `spdd-analysis` appends `## Analysis` to the issue body. Canvas files are prefixed `GH-<n>`. | The remote is on GitHub and the team works from issues |
| **File mode** | The requirement and analysis live in `{{ANALYSIS_DIR}}/<slug>.md` (default `spdd/analysis`). Canvas files are prefixed `<slug>`. | The project has no tracker, or uses one other than GitHub (GitLab, Jira, Linear). Paste or link the ticket into the requirement file. |

Issue mode turns on the `issue` flag. Issue mode also prompts two follow-ups: whether the rules doc requires a label taxonomy (`taxonomy`), and whether a board status has to move (`board`).

## D2. Is there a size gate?

Some projects use SPDD only for large work (Cosmo: Effort 5 or more, read from the GitHub Project). Look in the rules doc for a threshold or exemption.

- Found: turn on `gate` (and `exempt` if needed) and copy the rule word for word. The generated skills warn and ask ("Continue anyway?") but never refuse.
- Not found: ask whether to add one. The default is no gate.

## D3. Is the canvas committed?

| Option | Meaning |
|--------|---------|
| **Ephemeral** (recommended in issue mode) | `{{CANVAS_DIR}}` is gitignored, never staged, and never named by path in commits, issues or PRs. A lost canvas is regenerated from the analysis and `git diff {{MAIN_BRANCH}}...HEAD`. Whatever only the canvas knew goes into code, tests or design docs. |
| **Committed** (recommended in file mode) | The canvas is versioned next to the code it describes and lands in the same commits. |

The choice decides the skill set through the `sync` flag. **Committed** generates `spdd-sync` (`sync` on): the canvas outlives the branch and is a design record, so it has to follow the code. **Ephemeral** does not (`sync` off). A drifted canvas only matters before more code is generated from it inside the branch, and there it is rebuilt from the analysis and `git diff {{MAIN_BRANCH}}...HEAD` by `spdd-reasons-canvas`.

If `.gitignore` already covers the canvas directory, the answer is Ephemeral. Ephemeral turns on `ephemeral`, and the rendering step adds the gitignore entry when it is missing.

**Conflict with the rules doc.** If the rules doc already gives `spdd-sync` a role (Cosmo's section 8 says it keeps an ephemeral canvas in line with the code while the branch is open), don't drop the skill silently. Show the conflict and ask which one changes: generate `spdd-sync` anyway (`sync` on with `ephemeral` on), or edit the rules doc to point at the stale-canvas rebuild in `spdd-reasons-canvas`.

**File mode keeps the analysis.** In file mode, `{{ANALYSIS_DIR}}` is always committed, because it is the requirement and the only input a lost canvas can be rebuilt from. Gitignore `{{CANVAS_DIR}}` only, never a parent of both (`spdd/`). If a parent is already ignored, move `{{ANALYSIS_DIR}}` out of it, or narrow the ignore rule.

## D4. Where do the skills go?

Use the skills directory the project already has (`.agents/skills/`, `.claude/skills/`, or another). If there is none, recommend `.agents/skills/`, which the `skills` CLI and most hosts read. Then ask whether to mirror each skill as a slash command in `.claude/commands/<name>.md`. Cosmo does this. The command file is the same body with the frontmatter `name: /<name>`, `id: <name>`, `category: Development` and the same `description`.
