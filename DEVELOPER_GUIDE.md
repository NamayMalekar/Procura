# Developer Guide & Code Architecture Map

Welcome to **Procura: AI Purchasing Agent**. This guide is written to help you understand every layer of the codebase, trace how decisions flow, and make changes or additions with confidence.

---

## 1. High-Level Architecture & Mental Model

Procura is **not** a conversational chatbot; it is an **autonomous operational agent**. It follows a strictly enforced closed-loop lifecycle:

```
[1. Trigger / Case] --> [2. Investigate Tools]
                              |
                              v
                   [3. Replenishment Math]
                              |
                              v
             [4. Pre-Action Sandbox Validation]
               |                           |
        (Violations? Fix)               (Passed)
               |                           v
               +<---------------- [5. Human Approval Threshold]
                                           |
                                       (Approved)
                                           v
                              [6. Execute with Supplier API]
                                           |
                                           v
                             [7. Post-Action Reality Verify]
                               |                           |
                       (Discrepancy?)                  (Matches)
                               |                           v
                    [Re-plan in Cycle 2]          [Complete & Saved]
```

### The Two Critical Feedback Loops
1. **Pre-Action Sandbox (`validate` in `agent/validator.py`):**
   - Before any purchase order is sent to a vendor, the agent clones the SQLite database into memory.
   - It simulates the proposed order on this sandbox copy and checks:
     - **Evidence:** Did the agent actually investigate demand, inventory, and suppliers first?
     - **Budget:** Does spending fit within the category limit?
     - **Storage:** Does physical volume fit inside the warehouse?
     - **Stock Ceiling:** Will stock stay <= 125% of target?
     - **Supplier Constraints:** MOQ, pack sizes, vendor availability, and reliability rating >= 0.75.
   - If blocked, structured error codes are returned to the brain to adjust the proposal.
2. **Post-Action Reality Check (`verify` in `agent/validator.py`):**
   - After the executor places orders via the supplier API, `verify()` re-reads the database.
   - If a supplier rejected the order (e.g., stale price quote in **S4b**) or only partially shipped (**S2a**), it initiates a new planning cycle with the failure details fed into the brain.

---

## 2. Codebase Map: Where Everything Lives

```
ai-purchasing-agent/
├── backend/
│   ├── app/
│   │   ├── core/                  # Global settings, business rules, exceptions
│   │   │   ├── config.py          # .env loader, DB paths, model names
│   │   │   ├── policy.py          # Knobs: approval limit ($10k), cover factor (1.25), reliability (0.75)
│   │   │   └── exceptions.py      # NotFound, InvalidState, BrainError
│   │   │
│   │   ├── commons/               # Shared utilities
│   │   │   ├── enums.py           # Decisions, Action types, PO statuses
│   │   │   ├── money.py           # Cents math (avoids floating point errors)
│   │   │   └── packs.py           # Pack size rounding (ceil_pack, floor_pack)
│   │   │
│   │   ├── database/              # SQLite data persistence
│   │   │   ├── schema.py          # Table definitions (inventory, POs, budgets, tickets)
│   │   │   ├── seed_data.py       # Initial mock data (products, nodes, suppliers)
│   │   │   └── store.py           # Single repository interface with Store.clone()
│   │   │
│   │   ├── domain/                # Pure mathematical calculations
│   │   │   └── planning.py        # Replenishment formula & Demand surge classifier
│   │   │
│   │   ├── integrations/          # External integrations
│   │   │   └── supplier_api.py    # Mock vendor API with real-world failure simulation
│   │   │
│   │   ├── agent/                 # The brain & lifecycle orchestration
│   │   │   ├── agent.py           # Main loop: Investigate -> Validate -> Execute -> Verify
│   │   │   ├── tools.py           # Read-only tool definitions
│   │   │   ├── validator.py       # Pre-action simulation & post-action verification
│   │   │   ├── executor.py        # Places/amends POs and writes audit log
│   │   │   └── brains/
│   │   │       ├── rules.py       # Deterministic buyer playbook (offline brain)
│   │   │       └── llm.py         # Claude 3.5 Sonnet prompt & tool-use brain
│   │   │
│   │   ├── evaluation/            # Automated test suite
│   │   │   ├── cases.py           # The 10 purchasing situations (S1a - S4b)
│   │   │   └── expectations.py    # Hand-written golden answers
│   │   │
│   │   └── main.py                # FastAPI app entry point & SPA static files
│   │
│   └── tests/                     # 26 automated Pytest tests
│
└── frontend/                      # React + Vite application
    ├── src/
    │   ├── features/console/      # Main operational agent cockpit
    │   ├── features/data/         # Live system database browser
    │   ├── features/evaluation/   # 10/10 automated evaluation scorecard
    │   └── styles/                # CSS design system (tokens, layout, components)
```

---

## 3. End-to-End Trace: What Happens When You Click "Run Agent"

Let's follow what happens in **Scenario S4b** (Supplier rejects first order due to price hike):

1. **Frontend Request:** The UI calls `POST /api/runs` with `{"case_id": "S4b", "brain": "rules"}`.
2. **Cycle 1 - Investigation:** The agent calls 8 read-only tools:
   - `get_inventory`: On hand = 90, capacity = 2,000.
   - `get_demand`: Forecast = 50/day, last-7-day average = 50.1/day (normal demand).
   - `get_supplier_options`: Finds `SUP-8` (SunGold Oils, unit price $4.50, MOQ 500, pack 20).
   - `calculate_replenishment`: Target stock = 650, Net Need = 560 units.
3. **Cycle 1 - Proposal:** The brain proposes creating PO for 560 units with `SUP-8`.
4. **Cycle 1 - Pre-Validation:** `validator.validate()` runs on in-memory DB copy. All rules pass.
5. **Cycle 1 - Execution:** `executor.execute()` calls the mock vendor API.
   - The mock supplier API has an injected failure: *“Quote is stale. New unit price is $5.00.”* The order is marked `rejected`.
6. **Cycle 1 - Post-Verification:** `validator.verify()` inspects the real DB. It detects that the PO was rejected and stock is still 560 units short!
7. **Cycle 2 - Automated Recovery:**
   - The agent starts Cycle 2 with execution issues fed back to the brain.
   - The tools now report the updated price ($5.00).
   - The brain re-plans at $5.00, checks the budget ($5,000 limit allows $2,800), and re-submits.
   - Pre-validation passes, supplier confirms the second order (`PO-10002`).
   - Post-verification checks stock position = 650. Verification passes!
8. **Result Delivered:** The API returns status `completed` with full cycle ledger, which the frontend renders.

---

## 4. How-To Recipes (Common Changes)

### Recipe 1: Change Business Policies (Approval Limit, Safety Margins)
- Open `backend/app/core/policy.py`.
- **Change human approval threshold:** Modify `self.approval_threshold = 10000` (e.g. change to `5000` to require approval on orders over $5,000).
- **Change stock ceiling:** Modify `self.max_cover_factor = 1.25` (e.g. `1.15` for leaner stock).
- **Change minimum supplier reliability:** Modify `self.min_supplier_reliability = 0.75`.

### Recipe 2: Add a New Safety Rule to Pre-Action Validation
- Open `backend/app/agent/validator.py`.
- Find the `check_state(store, actions, tools_called, proposal)` function.
- Add your check:
  ```python
  # Example: Disallow ordering on Fridays for frozen goods
  if action["action"] == "create_po" and is_weekend_delivery(action["sku"]):
      issues.append({"code": "WEEKEND_RESTRICTION", "message": "Cannot order frozen items for weekend arrival."})
  ```
- If any violations are added to `issues`, the order is blocked automatically and sent back to the brain.

### Recipe 3: Add a New Purchasing Scenario
1. Open `backend/app/evaluation/cases.py`:
   - Add a new case dictionary with `id`, `scenario`, `title`, `trigger`, `sku`, `node`, `recommended_qty`.
2. Open `backend/app/evaluation/expectations.py`:
   - Add expected outcome: `decision`, `new_qty`, `suppliers`, and `status`.
3. If new products, nodes, or mock suppliers are needed, add them to `backend/app/database/seed_data.py`.
4. Run `npm run eval` to verify!

### Recipe 4: Enable the Claude LLM Brain
1. Create/edit `.env` in the root or `backend/`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-...
   AGENT_BRAIN=auto
   LLM_MODEL=claude-sonnet-5-5
   ```
2. Restart the app (`npm run start`). The UI will now enable the "Claude" option in the brain switcher.

---

## 5. Verification Commands

Always run these commands before submitting changes:
- `npm run test:backend`: Runs the 26 backend unit and scenario tests.
- `npm run eval`: Runs the 10/10 scenario evaluation scorecard.
- `npm run demo -- S4b`: Runs an end-to-end trace of a specific scenario in terminal.
- `npm run build`: Rebuilds the frontend bundle.
