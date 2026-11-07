# Codebase audit: jaoppb/skills (2026-11-07)

Scope: whole repo (~940 lines of Markdown, 4 skills, no executable code). The skill's fan-out to subagents was skipped because the repo is small enough to review in one pass. The checks follow the repo's own AGENTS.md checklist (section 4).

## Summary
Healthy and well-structured. Frontmatter parses, `name` matches the directory for all 4 skills, every relative link resolves, and README matches the tree. The gaps are in conformance to AGENTS.md's own rules and in missing automation.

## Strengths
- Progressive disclosure is applied well in `herdr-multi-agent` (lean root and 10 focused references).
- `herdr` and `grill-me` have clear negative bounds.

## Findings
| ID | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|
| AUD-001 | Medium | `thermo-nuclear-code-quality-review` description has no negative bounds (no "Do not use when"). Violates AGENTS 3.B/3.D and checklist item 3. | SKILL.md:3 | Add guardrails, e.g. not for ordinary reviews, bug-hunting, or small diffs unless a harsh review is asked for. |
| AUD-002 | Medium | `herdr-multi-agent` description has no explicit "Do not use when". It only has "Use only when". | SKILL.md:3 | Add "Do not use for a single agent or without Herdr". |
| AUD-003 | Low | Description format is inconsistent with the AGENTS.md template ("... Use when ... Do not use when ..."). `grill-me` and `thermo-nuclear...` are unquoted YAML, while the others are quoted. They parse today, but a later colon would break them. | frontmatter | Quote all four and follow the template. |
| AUD-004 | Low | Portability: `grill-me` hardcodes `AskUserQuestion`. `herdr-multi-agent` hardcodes `Agent`/`invoke_subagent` and `/thermo-nuclear...` (partly mitigated by "host's native capability"). Also `worker-prompts.md` writes briefs to `/tmp`. | grill-me:~60, review.md:6 | Phrase generically ("a structured-choice prompt if the host has one"). |
| AUD-005 | Low | No automated verification. The AGENTS.md checklist (frontmatter, name match, links, README sync) is manual and there is no CI. | no `.github/` | Add a small script/CI job that checks the four items. |
| AUD-006 | Low | The tree in README and the skill list in AGENTS.md are duplicated by hand and will drift. | README, AGENTS.md | Generate them, or keep a single source. |
| AUD-007 | Info | `.gitignore` lacks `.codebase-audit/`. | .gitignore | Add it if you keep audit output locally. |

Not-a-finding: my link scan flagged `AGENTS.md -> references/waves.md`; that is an illustrative example link, not a defect.

## Suggested order
AUD-001 and AUD-002 (small, high-value), then AUD-003, AUD-005, AUD-004.
