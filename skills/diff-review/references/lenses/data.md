# Data Lens

- **Role**: DBA / Data Engineer — schema compatibility, migration safety, query correctness, transactions, and PII hygiene.
- **Tier**: `flagship`
- **Activation Trigger**: Diff touches database migrations, schemas, ORM models, SQL/NoSQL queries, indexes, seed/backfill scripts, transaction boundaries, or PII storage/retention. Stay off when no persistence or data-schema code changes.
- **Delta Re-run Invalidation**:
  - `**/migrations/**`, `**/schema*`, `**/models/**`, `**/db/**`, `**/*.sql`, `**/prisma/**`, `**/drizzle/**`
  - Repository/DAO/query modules and backfill scripts
  - *Conservative fallback*: re-run whenever uncertain whether a change alters persistence or data contracts.

## Check

- **Migration safety & reversibility**: Is the migration safe to run zero-downtime against live traffic (expand-and-contract vs. destructive `DROP`/`RENAME`/non-null without default)? Does it acquire long table locks? Is rollback or forward-recovery clear?
- **Backward/forward compatibility**: Will old application instances crash while the migration is running or before the rollout completes?
- **Query & index safety**: Are new queries backed by appropriate indexes? Any full table scans, unbounded `SELECT`s without `LIMIT`/pagination, or N+1 query loops?
- **Transactions & atomicity**: Can multi-step writes leave partial/corrupt state on failure or concurrent access? Are isolation/locking assumptions explicit?
- **Data integrity & PII**: Are foreign keys, unique constraints, and nullability enforced at the schema level where invariants matter? Is PII minimized, masked in logs, and handled per retention rules?

## Presumptive Blockers

- **`blocker` (P0)**: Destructive/data-losing migration without safe expand-contract path, table-locking migration on hot tables without guard, non-atomic partial-write corruption on critical state, or unmasked PII leak.
- **`material` (P1)**: Missing index on queried columns, unbounded query/backfill, N+1 query in a loop, missing transaction around coupled writes, or missing constraint for a core invariant.
