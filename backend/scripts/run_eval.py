"""python -m scripts.run_eval  -> scorecard for every scenario."""
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
