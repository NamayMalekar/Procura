"""python -m scripts.run_eval  -> scorecard for every scenario."""
import sys
from pathlib import Path

# Allow direct script execution (e.g. python scripts/run_eval.py or python backend/scripts/run_eval.py)
_backend_dir = Path(__file__).resolve().parents[1]
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.evaluation.scorer import evaluate_all

if __name__ == "__main__":
    rep = evaluate_all()
    for r in rep["results"]:
        print(f"{'PASS' if r['pass'] else 'FAIL'}  {r['case']['id']}  {r['case']['title']}  "
              f"[{r['decision']}, {r['cycles']} cycle(s), {r['status']}]")
        for c in r["checks"]:
            if not c["pass"]:
                print(f"      x {c['check']}: {c['detail']}")
    print(f"\n{rep['passed']}/{rep['total']} scenarios passed")
