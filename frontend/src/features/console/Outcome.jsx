import Chip from '../../commons/Chip'
import { DECISION, STATUS, money } from '../../core/labels'

export default function Outcome({ run }) {
  const [label, tone] = STATUS[run.status] || [run.status, '']
  const cycle = run.cycles[run.cycles.length - 1]
  const metrics = cycle.attempts[cycle.attempts.length - 1]?.verdict?.metrics
  const cost = cycle.attempts[cycle.attempts.length - 1]?.verdict?.total_cost
  return (
    <div className="card outcome">
      <div className="eyebrow">Outcome &nbsp; <Chip tone={tone}>{label}</Chip> &nbsp;<Chip>{run.brain === 'llm' ? 'Claude' : 'Built-in rules'}</Chip></div>
      <div className="decision">{DECISION[run.decision] || run.decision}</div>
      <p className="why">{run.rationale}</p>
      {metrics && (
        <div className="stats">
          <div className="stat"><span className="eyebrow">Stock position</span>
            <b className="num">{metrics.before.position} &rarr; {metrics.after.position}</b></div>
          <div className="stat"><span className="eyebrow">Target</span><b className="num">{metrics.after.target}</b></div>
          <div className="stat"><span className="eyebrow">Order value</span><b className="num">{money(cost || 0)}</b></div>
          <div className="stat"><span className="eyebrow">Budget left</span><b className="num">{money(metrics.after.budget_remaining)}</b></div>
        </div>
      )}
      <h3>Why the agent decided this</h3>
      <ul className="factors">{run.factors.map((f, i) => <li key={i}>{f}</li>)}</ul>
      {run.escalation && (
        <div className="callout">
          <b>Buyer follow-up needed.</b> {run.escalation.reason}
          {run.escalation.follow_up && <><br />{run.escalation.follow_up}</>}
        </div>
      )}
      {run.notes?.map((n, i) => <p key={i} className="muted" style={{ marginTop: 12 }}>{n}</p>)}
    </div>
  )
}
