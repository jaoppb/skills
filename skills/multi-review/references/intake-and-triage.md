# Intake and triage (Coordinator)

Before spawning any reviewer workers, the coordinator intakes the pull request queue, triages it, assigns `lenses`, and confirms the plan with the person.

## 1. Intake the PR queue

Gather the target PRs from the person's request (explicit PR numbers/URLs, a release milestone, or open PRs via `gh pr list`):

```bash
gh pr list --state open --json number,title,author,isDraft,baseRefName,headRefName,additions,deletions,changedFiles,labels,reviewDecision
```

For each candidate PR, inspect its changed files (`gh pr view <N> --json files,body,url,statusCheckRollup`) so triage is grounded in real diff scope rather than titles alone.

## 2. Triage and prioritize

- **Filter or flag**: Mark draft PRs, PRs with failing required CI checks, or bot/automated PRs clearly so the person can decide whether to include, defer, or skip them.
- **Note stacked PRs**: If PR B targets PR A's branch (`baseRefName != main`), note the dependency so reviewers diff against `origin/<baseRefName>` and the coordinator highlights merge order in the final summary.
- **Prioritize**: Order the queue by risk and blast radius (security/data/core architecture changes and larger diffs first, small docs/chore PRs after) or by the person's explicit priority.
- **v1 scope**: Assign **one PR per worker**. Do not split a single PR across multiple Herdr workers (`diff-review` already fans out one fresh read-only sub-agent per active lens inside each worker).

## 3. Assign `lenses` and effort preset

For each PR in the queue, assign:
- **Content-aware baseline** from `diff-review`: `code-quality` for code PRs, `docs-quality` for docs-only PRs, or both for mixed PRs with substantial documentation changes.
- **Conditional specialist lenses** (`testing`, `security`, `data`, `devops`, `observability`, `frontend`, `seo`, `product-owner`, `product-manager`, `performance`, `api-docs`) triggered by the PR's changed files, plus any discovered external specialist agents.
- **Effort preset** from [agent-effort.md](agent-effort.md) (default **Preset 2**: Coordinator = Middle, Worker = Fast; opt-in Top worker only for unusually large or high-risk PRs).

## 4. Confirm before spawning

Present the triaged table (PR number, title, base branch, size, CI/draft status, assigned `lenses`, and effort preset) to the person using the host's ask protocol and wait for confirmation before creating worktrees or spawning workers.
