# Slicing & Dependencies Lens

- **Role**: Engineering Manager / Technical Program Lead — vertical slicing, ticket sizing, dependency DAG correctness, and parallel wave safety.
- **Tier**: `flagship`
- **Activation Trigger**: Multi-issue breakdown, epic decomposition, backlog refinement batch, or parallel wave plan (2+ work items). Stay off for a single standalone RFC, ADR, or isolated ticket.
- **Delta Re-run Invalidation**:
  - Any revision that adds, removes, splits, merges, reorders, or changes the scope/touched files/dependencies of any issue or wave
  - *Conservative fallback*: re-run whenever a revision alters task boundaries or ordering.

---

## Primary Review Questions

- **Vertical slicing vs. brittle horizontal layers**: Does each issue deliver a coherent, independently verifiable slice (or explicitly justified foundation), rather than slicing awkwardly into un-testable layers ("all DB models", "all UI", "all tests")?
- **Ticket sizing & decomposability**: Is any single issue actually an epic in disguise (too many orthogonal responsibilities, guaranteed >1k LOC sprawl), or conversely over-fragmented into micro-tickets that cannot be verified independently?
- **Dependency DAG integrity**: Are all prerequisites explicitly declared? Are there circular dependencies, missing foundational tickets, or inverted ordering?
- **Parallel wave & file-overlap safety**: For tasks intended to run in parallel (including `herdr-multi-agent` waves), do they touch the same files, schemas, registries, or shared contracts in ways that guarantee merge conflicts or semantic collisions?
- **End-to-end coverage across the breakdown**: If every child ticket is completed as written, does their union actually complete the parent epic without orphan wiring or leftover integration work?

---

## Severity Mapping

- **`blocker` (P0)**: Circular or broken dependency graph, missing prerequisite that blocks downstream tickets, two parallel-wave tickets that collide on the same core files/schemas/contracts, or a critical gap where completing all child issues still leaves the parent feature broken/unwired.
- **`material` (P1)**: Oversized ticket that should be split, un-testable horizontal slicing, missing dependency link, or over-fragmented tickets that should be merged.
- **`nitpick` (P2/P3)**: Minor ordering optimization or labeling/grouping clarity that does not affect correctness or parallelism.

Approve only with **zero `blocker` and zero `material` findings**.
