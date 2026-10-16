import Chip from '../../commons/Chip'
import Details from '../../commons/Details'
import { TOOL, describeAction } from '../../core/labels'

function Step({ tone = '', name, icon, children }) {
  return (
    <div className={`step-row ${tone}`}>
      <div className="step-timeline">
        <span className={`step-dot ${tone}`}>{icon}</span>
        <div className="step-line" />
      </div>
      <div className="step-body">
        <div className="step-title">{name}</div>
        <div className="step-content">{children}</div>
      </div>
    </div>
  )
}

function execLine(r) {
  const what = r.action === 'create_po' ? `Create PO ${r.po_id} (${r.requested} units)` : `Amend PO ${r.po_id}`
  if (r.status === 'confirmed' || r.status === 'ok') return `${what}: Confirmed by vendor`
  if (r.status === 'partial') return `${what}: Supplier accepted only ${r.confirmed} units (Shortfall)`
  return `${what}: ${r.status}${r.detail ? ` - ${r.detail}` : ''}`
}

function ToolCallSummary({ toolCalls }) {
  return (
    <div className="tool-calls-grid">
      {toolCalls.map((t, idx) => {
        const toolName = TOOL[t.tool] || t.tool
        return (
          <div key={idx} className="tool-pill">
            <span className="tool-name">{toolName}</span>
            <span className="tool-args">
              {Object.entries(t.args || {})
                .map(([k, v]) => `${k}=${v}`)
                .join(', ')}
            </span>
          </div>
        )
      })}
    </div>
  )
}

function Cycle({ cy }) {
  const v = cy.verification
  const tools = [...new Set(cy.tool_calls.map((t) => TOOL[t.tool] || t.tool))]
  const isReplanned = !!cy.feedback_in?.execution_issues

  return (
    <section className="cycle-container card">
      <header className="cycle-header">
        <div>
          <h4>
            Cycle {cy.cycle}
            {isReplanned && <span className="cycle-badge-replan"> (Automated Re-plan after supplier mismatch)</span>}
          </h4>
          <span className="muted" style={{ fontSize: '13px' }}>
            {cy.tool_calls.length} fact checks &bull; {cy.attempts.length} proposal attempt(s)
          </span>
        </div>
        {v ? (
          <Chip tone={v.ok ? 'ok' : 'bad'}>
            {v.ok ? '✓ Reality Verified' : '⚠️ Discrepancy Detected'}
          </Chip>
        ) : (
          <Chip>Decision Completed</Chip>
        )}
      </header>

      <div className="cycle-steps">
        <Step tone="ok" name="1. Investigate Market & Store State" icon="🔍">
          <p className="muted" style={{ marginBottom: '8px' }}>
            Queried <b>{tools.join(', ')}</b> ({cy.tool_calls.length} tool calls executed).
          </p>
          <ToolCallSummary toolCalls={cy.tool_calls} />
          <Details label="View raw tool data payload" data={cy.tool_calls} />
        </Step>

        {cy.attempts.map((a) => (
          <div key={a.attempt} className="attempt-block">
            <Step tone="ok" name={cy.attempts.length > 1 ? `2. Order Proposal (Attempt ${a.attempt})` : '2. Order Proposal'} icon="📋">
              <div className="proposal-desc">
                {a.proposal.actions.length ? (
                  <ul className="action-list">
                    {a.proposal.actions.map((act, i) => (
                      <li key={i} className="action-item">
                        <b>{act.action.toUpperCase()}</b>: {describeAction(act)}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="muted">No purchase orders placed (Demand covered or spike unverified).</p>
                )}
              </div>
            </Step>

            <Step tone={a.verdict.ok ? 'ok' : 'bad'} name="3. In-Memory Sandbox Safety Check" icon="🛡️">
              {a.verdict.ok ? (
                <div className="safety-ok">
                  <span>✓ All safety checks passed in sandbox simulation:</span>
                  <div className="constraint-tags">
                    <span className="chip ok">Budget within limit</span>
                    <span className="chip ok">Storage fits warehouse</span>
                    <span className="chip ok">MOQ & Pack size respected</span>
                    <span className="chip ok">Stock &le; 125% target</span>
                    <span className="chip ok">Reliable supplier (&ge; 0.75)</span>
                  </div>
                </div>
              ) : (
                <div className="safety-blocked">
                  <span className="badge-blocked">BLOCKED BY VALIDATOR</span>
                  <p className="muted" style={{ marginTop: '4px' }}>
                    Proposal violates business policy and was blocked before reaching any vendor:
                  </p>
                  <ul>
                    {a.verdict.violations.map((x, i) => (
                      <li key={i}>
                        <b>{x.code}</b>: {x.message}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </Step>
          </div>
        ))}

        {cy.approval && (
          <Step tone="ok" name="Human Buyer Sign-off" icon="👤">
            <p>Order exceeded financial threshold and was approved by the buyer. Re-validated against real-time data before placement.</p>
          </Step>
        )}

        {cy.execution && (
          <Step tone={cy.execution.every((r) => ['confirmed', 'ok'].includes(r.status)) ? 'ok' : 'warn'} name="4. Execute with Vendor API" icon="⚡">
            {cy.execution.length ? (
              <ul className="exec-list">
                {cy.execution.map((r, i) => (
                  <li key={i} className={`exec-item ${r.status}`}>
                    <span className={`chip ${r.status === 'confirmed' || r.status === 'ok' ? 'ok' : r.status === 'partial' ? 'warn' : 'bad'}`}>
                      {r.status.toUpperCase()}
                    </span>
                    <span>{execLine(r)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted">No external supplier actions needed.</p>
            )}
          </Step>
        )}

        {v && (
          <Step tone={v.ok ? 'ok' : 'bad'} name="5. Post-Action Reality Verification" icon="🎯">
            {v.ok ? (
              <div className="verify-ok">
                <span className="chip ok">✓ Reality Matches Simulated Plan</span>
                <p className="muted" style={{ marginTop: '6px' }}>
                  Confirmed stock position is <b>{v.actual.position}</b> against target of <b>{v.actual.target}</b> units.
                </p>
              </div>
            ) : (
              <div className="verify-diff">
                <span className="chip bad">⚠️ Reality Differed from Simulated Plan</span>
                <p className="muted" style={{ marginTop: '6px' }}>
                  Discrepancy detected between database and expected outcome:
                </p>
                <ul>
                  {v.issues.map((x, i) => (
                    <li key={i}>
                      <b>{x.code}</b>: {x.message}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </Step>
        )}
      </div>
    </section>
  )
}

export default function Ledger({ run }) {
  return (
    <div className="ledger-wrapper">
      <h3 className="ledger-title">
        Audit & Execution Ledger ({run.cycles.length} cycle{run.cycles.length > 1 ? 's' : ''})
      </h3>
      {run.cycles.map((cy) => (
        <Cycle key={cy.cycle} cy={cy} />
      ))}
    </div>
  )
}
