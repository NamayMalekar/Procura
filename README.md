# AI Purchasing Agent

A full-stack agent that **makes, executes and validates** purchasing decisions for a quick-commerce buyer.
It does not just answer questions: it investigates data with tools, decides, places or amends purchase orders,
then checks that reality matches what it expected, and retries or escalates when it does not.

All four scenarios are implemented end-to-end on mock data (10 test cases). It runs fully offline with a built-in
rules brain, and optionally with Claude as the brain.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # optional: add ANTHROPIC_API_KEY to use Claude
uvicorn backend.main:app --reload                      # open http://localhost:8000
```
Terminal demo (no UI needed): `python -m evals.demo` (saved output: [docs/DEMO_OUTPUT.md](docs/DEMO_OUTPUT.md))

Run the tests: `pytest -q` &nbsp;|&nbsp; Terminal scorecard: `python -m evals.run_eval`

## How it works
![Architecture](docs/architecture.svg)

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). File-by-file map: [FILE_GUIDE.md](FILE_GUIDE.md).

1. **Investigate.** The brain calls read-only tools: inventory, demand (with surge vs one-day-spike detection),
   promotions, open POs, supplier options, budget, replenishment calculator. Every call is logged.
2. **Decide.** It never trusts the incoming recommendation. It computes the real need:
   `target = effective daily demand x (lead time + review period) + safety stock`, `need = target - (on hand + incoming)`,
   then fits the order to MOQ, case size, supplier stock, budget and storage. Output: accept, modify, reject,
   investigate or escalate, with factors and optional actions (`create_po`, `amend_po`, `cancel_po`).
3. **Validate (before acting).** Plain-code validator simulates the proposal on a copy of the data and checks
   constraints plus evidence. Failures go back to the brain.
4. **Approve.** Orders above the threshold wait for a human click; the proposal is re-validated after approval.
5. **Act.** Executor talks to the mock supplier API.
6. **Verify (after acting).** POs are read back and the real stock position is compared to the simulated one.
   Rejections, partial fills or mismatches trigger another cycle; after 3 cycles a buyer ticket is raised.

## Scenarios covered
| Case | Situation | Expected behaviour |
|---|---|---|
| S1a | Recommendation of 800 is right | accept |
| S1b | Open PO already covers demand | reject |
| S1c | Recommendation too large | modify to 600 |
| S1d | Other node already well stocked | reject |
| S2a | Supplier ships 250 of 500, stock low | amend PO, source 290 from reliable alternate (skips the cheap unreliable one) |
| S2b | Supplier ships 250 of 500, stock enough | amend PO only, no new order |
| S3a | Sales 2.3x forecast for a week | trust data, top up 480 |
| S3b | One day of huge sales | do not buy, investigate and ticket the buyer |
| S4a | Budget limits buy to 450-500 of 800 | buy max affordable from cheaper supplier, escalate the gap |
| S4b | Supplier rejects first order (stale price) | verify fails, re-plan with new price, succeed in cycle 2 |

## Evaluation approach
- **Golden answers** are written by hand in `backend/evaluation.py`, not computed by the agent's code.
- Each scenario is scored on: decision correct, necessary information obtained, constraints respected
  (re-checked on the final data, independent of the validator), appropriate action taken, result validated,
  recovery from failure, final status.
- **Adversarial tests** (`tests/test_scenarios.py`): a brain that blindly accepts is blocked and nothing is ordered;
  a brain that skips investigation is rejected; a brain fixes itself from validator feedback; supplier rejection and
  partial fills trigger re-planning; no alternate supplier leads to escalation; unreliable suppliers are never used;
  large orders wait for approval.
- Using Claude as the brain: run the same scorecard with `evaluate_all(brain_factory=LLMBrain)`.

## Limits and ideas
Mock data, in-memory store, single process. Easy extensions: stock transfer between nodes as a new action
(`executor.py` + `tools.py`), supplier reliability scoring from past POs, promotional buying, seasonality in `planning.py`.

Do not commit `.env`. Commit in small steps so the history shows how the solution evolved.
