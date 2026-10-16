import Chip from '../../commons/Chip'
import { DECISION, STATUS, money } from '../../core/labels'

const DECISION_META = {
  accept: { tone: 'ok', title: 'Recommendation Accepted', icon: '✓', subtitle: 'Matches real calculated demand & respects all constraints.' },
  modify: { tone: 'accent', title: 'Plan Modified & Right-Sized', icon: '⚡', subtitle: 'Adjusted to fit true replenishment needs, MOQ, and storage.' },
  reject: { tone: '', title: 'Purchase Rejected', icon: '✕', subtitle: 'Existing inventory and open pipeline already cover demand.' },
  investigate: { tone: 'warn', title: 'Flagged for Buyer Investigation', icon: '?', subtitle: 'Spike volume not proven sustained; holding purchase.' },
  escalate: { tone: 'bad', title: 'Escalated to Buyer', icon: '!', subtitle: 'Real need cannot be met within budget or supply limits.' },
}

export default function Outcome({ run }) {
  const [statusLabel, statusTone] = STATUS[run.status] || [run.status, '']
  const cycle = run.cycles[run.cycles.length - 1]
  const metrics = cycle?.attempts[cycle.attempts.length - 1]?.verdict?.metrics
  const cost = cycle?.attempts[cycle.attempts.length - 1]?.verdict?.total_cost
  const decMeta = DECISION_META[run.decision] || { tone: '', title: run.decision, icon: '•', subtitle: '' }

  return (
    <div className="card outcome-card">
      <div className="outcome-header">
        <div>
          <span className="eyebrow" style={{ color: 'var(--accent)' }}>Decision Outcome</span>
          <div className="outcome-title-row">
            <span className={`decision-badge ${decMeta.tone}`}>
              <span className="dec-icon">{decMeta.icon}</span>
              {DECISION[run.decision] || run.decision}
            </span>
            <Chip tone={statusTone}>{statusLabel}</Chip>
            <Chip>{run.brain === 'llm' ? 'Claude Sonnet' : 'Built-in Rules Brain'}</Chip>
          </div>
        </div>
      </div>

      <div className="outcome-rationale-box">
        <p className="rationale-text">{run.rationale}</p>
        <span className="rationale-sub">{decMeta.subtitle}</span>
      </div>

      {metrics && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Stock Position</span>
            <div className="stat-value">
              <span className="num">{metrics.before.position}</span>
              <span className="stat-arrow">&rarr;</span>
              <span className="num" style={{ color: 'var(--accent)' }}>{metrics.after.position}</span>
            </div>
            <span className="stat-desc">Before &rarr; After Execution</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Target Position</span>
            <div className="stat-value num">{metrics.after.target}</div>
            <span className="stat-desc">Daily demand &times; lead + safety</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Purchase Value</span>
            <div className="stat-value num" style={{ color: cost > 0 ? 'var(--ink)' : 'var(--muted)' }}>
              {money(cost || 0)}
            </div>
            <span className="stat-desc">{cost > 0 ? 'Total committed spend' : 'Zero spend committed'}</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Budget Remaining</span>
            <div className="stat-value num" style={{ color: metrics.after.budget_remaining < 1000 ? 'var(--warn)' : 'var(--ok)' }}>
              {money(metrics.after.budget_remaining)}
            </div>
            <span className="stat-desc">Category balance</span>
          </div>
        </div>
      )}

      <div className="factors-section">
        <h4>Decision Evidence & Rationales</h4>
        <div className="factors-list">
          {run.factors.map((f, i) => (
            <div key={i} className="factor-item">
              <span className="factor-check">✓</span>
              <span className="factor-text">{f}</span>
            </div>
          ))}
        </div>
      </div>

      {run.escalation && (
        <div className="escalation-alert">
          <div className="esc-header">
            <b>⚠️ Buyer Action Required:</b>
          </div>
          <div className="esc-body">
            <p>{run.escalation.reason}</p>
            {run.escalation.follow_up && (
              <p className="esc-followup">
                <b>Recommended Next Step:</b> {run.escalation.follow_up}
              </p>
            )}
          </div>
        </div>
      )}

      {run.notes?.map((n, i) => (
        <p key={i} className="muted" style={{ marginTop: 12, fontSize: '13px' }}>
          ℹ️ {n}
        </p>
      ))}
    </div>
  )
}
