# Slicing & Dependencies Lens

- **Role**: Engineering Manager / Technical Program Lead — vertical slicing, ticket sizing, dependency DAG correctness, and concurrent task safety.
- **Tier**: `fast/balanced`
- **Activation Trigger**: Multi-issue breakdown, epic decomposition, backlog refinement batch, or task dependency graph (2+ work items). Stay off for a single standalone RFC, ADR, or isolated ticket.
- **Delta Re-run Invalidation**:
  - Any revision that adds, removes, splits, merges, reorders, or changes the scope/touched files/dependencies/edges of any issue in the graph
  - *Conservative fallback*: re-run whenever a revision alters task boundaries or ordering.

## Check

- **Vertical slicing vs. brittle horizontal layers**: Does each issue deliver a coherent, independently verifiable slice (or explicitly justified foundation), rather than slicing awkwardly into un-testable layers ("all DB models", "all UI", "all tests")?
- **Ticket sizing & decomposability**: Is any single issue actually an epic in disguise (too many orthogonal responsibilities, guaranteed >1k LOC sprawl), or conversely over-fragmented into micro-tickets that cannot be verified independently?
- **Dependency DAG integrity**: Are all prerequisites explicitly declared? Are there circular dependencies, missing foundational tickets, or inverted ordering?
- **Concurrency & file-overlap safety**: For tasks that can run concurrently (unblocked tasks with no dependency or overlap edge between them, including `multi-implement` graphs), do they touch the same files, schemas, registries, or shared contracts in ways that guarantee merge conflicts or semantic collisions?
- **End-to-end coverage across the breakdown**: If every child ticket is completed as written, does their union actually complete the parent epic without orphan wiring or leftover integration work?

## Presumptive Blockers

- **`blocker` (P0)**: Circular or broken dependency graph, missing prerequisite that blocks downstream tickets, two concurrent (unblocked) tickets with no dependency or overlap edge between them that collide on the same core files/schemas/contracts, or a critical gap where completing all child issues still leaves the parent feature broken/unwired.
- **`material` (P1)**: Oversized ticket that should be split, un-testable horizontal slicing, missing dependency link, or over-fragmented tickets that should be merged.
