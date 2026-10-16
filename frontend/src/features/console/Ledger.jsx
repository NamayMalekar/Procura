import Chip from '../../commons/Chip'
import Details from '../../commons/Details'
import { TOOL, describeAction } from '../../core/labels'

function Step({ tone = '', name, children }) {
  return (
    <div className="step">
      <span className={`dot ${tone}`} />
      <span className="name">{name}</span>
      <div>{children}</div>
    </div>
  )
}

function execLine(r) {
  const what = r.action === 'create_po' ? `${r.po_id}, ${r.requested} units` : `${r.po_id}`
  if (r.status === 'confirmed' || r.status === 'ok') return `${what}: confirmed`
  if (r.status === 'partial') return `${what}: supplier shipped only ${r.confirmed}`
  return `${what}: ${r.status}${r.detail ? ` (${r.detail})` : ''}`
}

function Cycle({ cy }) {
  const v = cy.verification
  const tools = [...new Set(cy.tool_calls.map((t) => TOOL[t.tool] || t.tool))]
  return (
    <section className="cycle">
      <header>
        <h4>Cycle {cy.cycle}{cy.feedback_in?.execution_issues ? ' (re-plan after a failed check)' : ''}</h4>
        {v ? <Chip tone={v.ok ? 'ok' : 'bad'}>{v.ok ? 'Verified' : 'Result differed from plan'}</Chip> : <Chip>Not executed</Chip>}
      </header>
      <Step tone="ok" name="Investigate">
        Looked at {tools.join(', ')} ({cy.tool_calls.length} checks).
        <Details label="Show every check" data={cy.tool_calls} />
      </Step>
      {cy.attempts.map((a) => (
        <div key={a.attempt}>
          <Step tone="ok" name={cy.attempts.length > 1 ? `Proposal ${a.attempt}` : 'Proposal'}>
            {a.proposal.actions.length ? a.proposal.actions.map(describeAction).join('; ') : 'No order placed.'}
          </Step>
          <Step tone={a.verdict.ok ? 'ok' : 'bad'} name="Safety check">
            {a.verdict.ok ? 'All rules passed: budget, storage, supplier limits, stock ceiling.' : 'Blocked, sent back to the agent:'}
            {!a.verdict.ok && <ul>{a.verdict.violations.map((x, i) => <li key={i}><b>{x.code}</b>: {x.message}</li>)}</ul>}
          </Step>
        </div>
      ))}
      {cy.approval && <Step tone="ok" name="Approval">Approved by you. Re-checked against the latest data before placing.</Step>}
      {cy.execution && (
        <Step tone={cy.execution.every((r) => ['confirmed', 'ok'].includes(r.status)) ? 'ok' : 'warn'} name="Execute">
          {cy.execution.length ? <ul>{cy.execution.map((r, i) => <li key={i}>{execLine(r)}</li>)}</ul> : 'Nothing to place.'}
        </Step>
      )}
      {v && (
        <Step tone={v.ok ? 'ok' : 'bad'} name="Verify">
          {v.ok ? `Reality matches the plan. Stock position is ${v.actual.position} against a target of ${v.actual.target}.`
            : <>Reality differed from the plan:<ul>{v.issues.map((x, i) => <li key={i}><b>{x.code}</b>: {x.message}</li>)}</ul></>}
        </Step>
      )}
    </section>
  )
}

export default function Ledger({ run }) {
  return (
    <>
      <h3 className="ledger-title">What the agent did</h3>
      {run.cycles.map((cy) => <Cycle key={cy.cycle} cy={cy} />)}
    </>
  )
}
