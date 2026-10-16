# Architecture

![Architecture](architecture.svg)

## Layers (same idea as CityCare / Stayvo)
```
frontend (React)  ->  api/routes  ->  services  ->  agent  ->  database (SQLite)
                                                      |-> domain (pure math)
                                                      |-> integrations (mock supplier)
core (settings, policy) and commons (enums, money, packs, schemas) are shared by all layers
```

## The two feedback loops
1. **Before acting.** The brain proposes. `validate()` copies the database (`Store.clone()`), applies the proposal to the
   copy, and checks budget, storage, stock ceiling, MOQ, case size, supplier stock, supplier reliability,
   evidence gathered and unaddressed shortfall. Violations go back to the brain (max 3 attempts).
2. **After acting.** The executor does it for real. `verify()` reads the purchase orders back and compares the real stock
   position with the simulated one. A rejected or partial supplier answer, or any mismatch, starts a new cycle with the
   failure as feedback (max 3 cycles), then a ticket is raised for a human buyer.

## Why the validator is plain code
The brain (rules or LLM) can be wrong. The validator is deterministic, so an unsafe order cannot reach a supplier even if the
brain is confidently incorrect. Tests prove it with brains that are deliberately wrong.

## Human approval
Orders above `APPROVAL_THRESHOLD` pause as `pending_approval`. Runs are stored in the database, so approval works even after a
page reload. On approval the proposal is validated again, because data may have changed.

## Data model (SQLite)
nodes, products, suppliers, inventory, demand, promotions, supplier_items, budgets, purchase_orders, escalations, audit_log,
agent_runs, meta. See `backend/app/database/schema.py`.
