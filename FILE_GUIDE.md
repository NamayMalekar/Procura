# Which file has which code

The project follows the same layered idea as CityCare and Stayvo:
**core** (settings and rules), **commons** (shared helpers), **database** (all data access), then the feature layers on top.
Each layer only talks to the layers below it.

```
api/routes  ->  services  ->  agent  ->  database  ->  SQLite file
                                |-> domain (math)   |-> integrations (mock supplier)
core + commons are used by everyone
```

## backend/app/

### core/  (settings and business rules)
| File | What is inside | Edit it to... |
|---|---|---|
| `core/config.py` | Environment settings: database path, API key, which brain, model name | change a setting |
| `core/policy.py` | Business rules: approval limit, stock ceiling, minimum supplier reliability, retry limits | change a policy number |
| `core/exceptions.py` | The error types (NotFound, InvalidState, BrainError) | add a new error type |

### commons/  (shared helpers, used everywhere)
| File | What is inside |
|---|---|
| `commons/enums.py` | Fixed words: decisions, run statuses, PO statuses, action types |
| `commons/money.py` | Money in whole cents (avoids decimal bugs) |
| `commons/packs.py` | Round quantities to supplier case sizes |
| `commons/schemas.py` | The shapes of API request bodies |

### database/  (all data access, SQLite)
| File | What is inside | Edit it to... |
|---|---|---|
| `database/schema.py` | Table definitions (the data model) | add a table or column |
| `database/seed_data.py` | The fake business data as plain Python | change stock, prices, budgets, suppliers |
| `database/seed.py` | Loads that data into the tables | rarely |
| `database/connection.py` | Opens SQLite, makes in-memory copies for what-if tests | rarely |
| `database/repositories/*.py` | One file per table group: catalog, inventory, supplier_items, budgets, purchase_orders, escalations, audit, runs | change a query |
| `database/store.py` | The single door to the database; the agent only talks to this | add a new read/write helper |

### domain/, integrations/
| File | What is inside | Edit it to... |
|---|---|---|
| `domain/planning.py` | The inventory math: target stock, real-surge vs one-day-spike detection | change how demand or target stock is calculated |
| `integrations/supplier_api.py` | The pretend supplier: yes, partly, or no, plus injected failures | add a new supplier failure type |

### agent/  (the thinking and acting)
| File | What is inside | Edit it to... |
|---|---|---|
| `agent/agent.py` | The main loop: investigate, safety check, approval, act, verify, retry, escalate | change retry/approval flow |
| `agent/tools.py` | Read-only tools the agent uses to investigate (and their descriptions for the LLM) | give the agent new information |
| `agent/validator.py` | `validate()` = safety checks before acting. `verify()` = did reality match the plan? | add or loosen a safety rule |
| `agent/executor.py` | The only code that creates/amends/cancels purchase orders and moves budget | add an action (e.g. stock transfer) |
| `agent/brains/rules.py` | Decision logic without AI (a buyer playbook) | change how it picks suppliers or decides |
| `agent/brains/llm.py` | The Claude version: instructions (`SYSTEM`) and answer format (`SUBMIT`) | change the AI's instructions |
| `agent/brains/__init__.py` | Chooses which brain to use | rarely |

### services/, api/, evaluation/
| File | What is inside | Edit it to... |
|---|---|---|
| `services/run_service.py` | Use-cases the API calls: start a run, approve a run | add a new use-case |
| `api/routes/*.py` | The web endpoints: runs, scenarios, state, evaluation, system | add an endpoint |
| `api/deps.py` | Gives routes access to the database and services | rarely |
| `main.py` | Builds the app and serves the React UI | rarely |
| `evaluation/cases.py` | The 10 test situations | add a scenario |
| `evaluation/expectations.py` | The hand-written correct answers | add a correct answer |
| `evaluation/scorer.py` | The scoring checks | add a new check |

## backend/ (outside app/)
| File | What is inside |
|---|---|
| `tests/test_scenarios.py` | Scenario tests, plus tests where the brain is wrong or the supplier misbehaves |
| `tests/test_database.py`, `tests/test_api.py` | Database layer and web API tests |
| `scripts/run_eval.py`, `scripts/demo.py` | Terminal scorecard and a readable story of each run |
| `.env.example`, `requirements.txt`, `pytest.ini` | Setup files |

## frontend/src/ (React)
| File | What is inside | Edit it to... |
|---|---|---|
| `styles/tokens.css` | All colours, fonts, radius, light and dark themes | restyle the whole app |
| `styles/base.css`, `layout.css`, `components.css` | Page reset, layout, component styles | change spacing or layout |
| `core/api.js` | Every call to the backend | add an API call |
| `core/theme.js` | Light/dark switch, remembered in the browser | rarely |
| `core/labels.js` | Plain-English wording for statuses, decisions and tools | change any wording |
| `commons/*.jsx` | Reusable parts: Button, Chip, Icon, Segmented, Switch, Details | add a shared component |
| `layout/AppShell.jsx` | Sidebar, brand, navigation, theme button | change navigation |
| `features/console/` | The main screen: scenario list, case brief, outcome, approval banner, step-by-step ledger | change the main screen |
| `features/data/DataPage.jsx` | System data tables (inventory, orders, budgets, tickets, audit) | add a table |
| `features/evaluation/EvaluationPage.jsx` | The evaluation scorecard screen | change the scorecard |
| `App.jsx`, `main.jsx` | Page switching and app start | rarely |

## Common changes
- **Stricter approval:** `APPROVAL_THRESHOLD` in `backend/.env` or `core/policy.py`
- **New product or supplier:** `database/seed_data.py`
- **New scenario:** add a case in `evaluation/cases.py` and its correct answer in `evaluation/expectations.py`
- **New safety rule:** `check_state()` in `agent/validator.py`
- **New thing the agent must always check first:** add a tool in `agent/tools.py`, call it in `agent/brains/rules.py`, list it in `EVIDENCE` in `agent/validator.py`
- **Change colours or fonts:** `frontend/src/styles/tokens.css`
