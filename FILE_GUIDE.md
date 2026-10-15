# Which file has which code

## Backend (`backend/`)
| File | What is inside (simple words) | Edit it when you want to... |
|---|---|---|
| `config.py` | Settings and business rules: approval limit, max stock ceiling, minimum supplier reliability, retry limits | change a policy number |
| `data.py` | All fake data: products, stock, sales, suppliers, budgets, open POs, and the 10 test cases (`CASES`) | add a product, change a number, add a new scenario |
| `planning.py` | The math: how much stock we want, whether a sales jump is real, rounding to case sizes | change how demand or target stock is calculated |
| `store.py` | The in-memory database and simple "look up X" helpers | add a new kind of data |
| `supplier_api.py` | Pretend supplier: says yes, partly yes, or no (and injects failures) | add a new kind of supplier failure |
| `executor.py` | The only code that creates, changes or cancels purchase orders and moves budget | add a new action (e.g. transfer stock between nodes) |
| `tools.py` | Read-only tools the agent uses to investigate, plus their descriptions for the LLM | give the agent a new source of information |
| `brain_rules.py` | The agent's decision logic without AI (a buyer playbook) | change how it picks suppliers or chooses accept/modify/reject |
| `brain_llm.py` | The Claude version of the brain: its instructions (`SYSTEM`) and answer format (`SUBMIT`) | change the AI instructions |
| `validator.py` | The safety checks before acting (`validate`) and the "did it work?" check after acting (`verify`) | add or loosen a safety rule |
| `agent.py` | The main loop: investigate, validate, ask human, act, verify, retry | change the retry or approval flow |
| `evaluation.py` | The scoring: correct answers for each scenario and the checks | add a test case or a new check |
| `main.py` | The web API (buttons in the UI call these URLs) | add a new endpoint |

## Frontend
| File | What is inside |
|---|---|
| `frontend/index.html` | The whole screen: CSS at the top, HTML in the middle, JavaScript at the bottom |

## Tests, docs, setup
| File | What is inside |
|---|---|
| `tests/test_scenarios.py` | Scenario tests, plus tests where the brain is wrong or the supplier misbehaves |
| `tests/test_api.py` | One test that calls the web API |
| `evals/run_eval.py` | Prints the scorecard in the terminal |
| `docs/ARCHITECTURE.md` | Architecture diagram and the two feedback loops |
| `.env.example` | Which environment variables exist (copy to `.env`) |
| `requirements.txt` | Python packages |

## Common changes
- **"Make approval stricter"** -> `APPROVAL_THRESHOLD` in `config.py` (or `.env`)
- **"Allow bigger overstock"** -> `MAX_COVER_FACTOR` in `config.py`
- **"Add a new product or supplier"** -> `data.py` (`products`, `inventory`, `demand`, `supplier_items`)
- **"Add a new scenario"** -> add a case in `CASES` (`data.py`) and its golden answer in `EXPECT` (`evaluation.py`)
- **"The agent should also check X before deciding"** -> add a tool in `tools.py`, then call it in `brain_rules.py`; list it in `EVIDENCE` in `validator.py` to make it mandatory
- **"New safety rule"** -> `check_state()` in `validator.py`
