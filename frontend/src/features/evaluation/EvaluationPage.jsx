import { useState } from 'react'
import Button from '../../commons/Button'
import Chip from '../../commons/Chip'
import Icon from '../../commons/Icon'
import { api } from '../../core/api'
import { DECISION, STATUS } from '../../core/labels'

const CHECK = {
  decision_correct: 'Decision was correct', got_necessary_information: 'Gathered the necessary information',
  respected_constraints: 'Respected every constraint', took_appropriate_action: 'Took the appropriate action',
  validated_result: 'Validated the result after acting', recovered_from_failure: 'Recovered from a failed first attempt',
  final_status: 'Ended in the expected state',
}

export default function EvaluationPage() {
  const [rep, setRep] = useState(null)
  const [busy, setBusy] = useState(false)
  const run = async () => { setBusy(true); try { setRep(await api.evaluation()) } finally { setBusy(false) } }

  return (
    <>
      <header className="page-head">
        <div><h1>Evaluation</h1>
          <p>Every situation runs on fresh data and is scored against hand-written correct answers: decision, evidence, constraints, action, validation and recovery.</p></div>
        <Button onClick={run} disabled={busy}><Icon name="play" size={14} /> {busy ? 'Running...' : rep ? 'Run again' : 'Run evaluation'}</Button>
      </header>
      {!rep && <div className="empty-state"><h3>No results yet</h3><p>Run the evaluation to score the agent on all {10} situations.</p></div>}
      {rep && (
        <>
          <div className="score"><b className="num">{rep.passed}/{rep.total}</b><span className="muted">situations passed every check</span></div>
          {rep.results.map((r) => (
            <details className="eval-row" key={r.case.id}>
              <summary>
                <span className="muted">{r.case.id}</span>
                <span><b>{r.case.title}</b> <span className="muted">&nbsp;{DECISION[r.decision]}, {r.cycles} cycle{r.cycles > 1 ? 's' : ''}</span></span>
                <Chip tone={(STATUS[r.status] || [])[1]}>{(STATUS[r.status] || [r.status])[0]}</Chip>
                <Chip tone={r.pass ? 'ok' : 'bad'}>{r.pass ? 'Pass' : 'Fail'}</Chip>
              </summary>
              <div className="checks">
                {r.checks.map((c) => (
                  <div className="check" key={c.check}>
                    <Chip tone={c.pass ? 'ok' : 'bad'}>{c.pass ? 'Pass' : 'Fail'}</Chip>
                    <span><b>{CHECK[c.check] || c.check}</b> <span className="muted">&nbsp;{c.detail}</span></span>
                  </div>
                ))}
              </div>
            </details>
          ))}
        </>
      )}
    </>
  )
}
