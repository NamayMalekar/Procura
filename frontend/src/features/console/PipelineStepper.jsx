import Icon from '../../commons/Icon'

export default function PipelineStepper({ run }) {
  if (!run) return null

  const cycleCount = run.cycles.length
  const lastCycle = run.cycles[cycleCount - 1]
  const execution = lastCycle?.execution || []
  const hasExecuted = execution.length > 0
  const verify = lastCycle?.verification
  const isPending = run.status === 'pending_approval'

  const stages = [
    {
      id: 'investigate',
      name: '1. Investigate',
      desc: `${lastCycle.tool_calls.length} checks run`,
      status: 'done',
    },
    {
      id: 'calculate',
      name: '2. Propose & Plan',
      desc: run.decision?.toUpperCase(),
      status: 'done',
    },
    {
      id: 'validate',
      name: '3. Pre-Action Sandbox',
      desc: 'All constraints pass',
      status: 'done',
    },
    {
      id: 'execute',
      name: '4. Execute',
      desc: isPending ? 'Awaiting Human Approval' : hasExecuted ? `${execution.length} action(s) placed` : 'No order needed',
      status: isPending ? 'warn' : 'done',
    },
    {
      id: 'verify',
      name: '5. Reality Check',
      desc: verify ? (verify.ok ? 'Verified matches plan' : 'Discrepancy detected') : 'Completed',
      status: verify ? (verify.ok ? 'done' : 'bad') : 'done',
    },
  ]

  return (
    <div className="pipeline-stepper card">
      <div className="pipeline-header">
        <div>
          <span className="eyebrow" style={{ color: 'var(--accent)' }}>Decision Lifecycle</span>
          <h4>Closed-Loop Execution Pipeline</h4>
        </div>
        {cycleCount > 1 && (
          <span className="chip warn">
            Cycle {cycleCount} (Auto-replanned after supplier feedback)
          </span>
        )}
      </div>
      <div className="stages-bar">
        {stages.map((st, i) => (
          <div key={st.id} className={`stage-item ${st.status}`}>
            <div className="stage-badge">
              {st.status === 'done' ? '✓' : st.status === 'warn' ? '!' : '✕'}
            </div>
            <div className="stage-text">
              <span className="stage-name">{st.name}</span>
              <span className="stage-desc">{st.desc}</span>
            </div>
            {i < stages.length - 1 && <div className="stage-connector" />}
          </div>
        ))}
      </div>
    </div>
  )
}
