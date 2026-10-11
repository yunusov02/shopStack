# Domain rules

The roadmap's "Domain rules" apply to the whole project. In review, violating any of them is a 🔴 (must fix).

- **Money:** only `Decimal` (`Numeric(p, s)` in the DB) or integer minor units (tiyin). Never `float`, not even in tests.
- **Quantity:** `Decimal(12, 3)` for weighted products.
- **Time:** UTC and timezone-aware only. Use `datetime.now(UTC)`; `datetime.utcnow()` and naive datetimes are forbidden. Use `timestamptz` in the DB. The tenant's time zone is only for display and for rules like "happy hour".
- **Stock decrements are synchronous:** a sale and its stock change happen in one ACID transaction, never through Celery or events.
- **Documents are immutable:** a completed sale, receipt, or transfer is never edited. Mistakes are corrected with a new document: a return, an adjustment, or a reversal (storno).
- **Snapshots:** a sale line stores price, cost, tax, and applied promotions as they were at the time of sale. Reading the current price through an FK is wrong.
- **Ledgers:** every balance (stock, customer balance, points, debt) is the sum of immutable entries. If a separate balance column exists, it is updated in the same transaction as the ledger entry and verified by reconciliation.
- **State machines:** every document has explicit states and allowed transitions, and transitions are logged. State changes go through a transition function, not a direct `obj.status = ...`.
- **Sensitive operations** (refund, void, manual discount, price change, adjustment) are protected by a permission and written to the audit log.
- **Multi-tenancy (from stage 1):**
  - every tenant-owned table has `tenant_id`;
  - filtering fails closed: with no tenant context, the result is an error, not all rows;
  - an object belonging to another tenant or location returns `404`, not `403`, because `403` reveals that the object exists.
- **Concurrency:** if a limit or balance check is "read → check → write", it needs a lock (`with_for_update`) or an atomic `UPDATE ... WHERE`. When locking several rows, always acquire them in the same order to avoid deadlocks.
- **Idempotency:** external requests that change money or stock are accepted with an `Idempotency-Key`.
