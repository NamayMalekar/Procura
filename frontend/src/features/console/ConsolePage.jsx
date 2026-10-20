import { useState } from 'react'
import { api } from '../../core/api'
import ApprovalBanner from './ApprovalBanner'
import CaseBrief from './CaseBrief'
import HowItWorksModal from './HowItWorksModal'
import Ledger from './Ledger'
import Outcome from './Outcome'
import PipelineStepper from './PipelineStepper'
import ScenarioList from './ScenarioList'

export default function ConsolePage({ cases, config, state, setState, onDataChanged, onReset }) {
  const { selected, run } = state
  const [brain, setBrain] = useState('rules')
  const [auto, setAuto] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [showGuide, setShowGuide] = useState(false)
  const item = cases.find((c) => c.id === selected)

  const guard = async (fn) => {
    setBusy(true)
    setError('')
    try {
      await fn()
      onDataChanged()
    } catch (e) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  const runAgent = () =>
    guard(async () =>
      setState({
        selected,
        run: await api.startRun({ case_id: selected, brain, auto_approve: auto }),
      })
    )

  const decide = (ok) =>
    guard(async () =>
      setState({ selected, run: await api.decide(run.run_id, ok) })
    )

  return (
    <>
      <HowItWorksModal open={showGuide} onClose={() => setShowGuide(false)} />

      <header className="page-head">
        <div>
          <div className="eyebrow" style={{ color: 'var(--accent)' }}>Operational Control Center</div>
          <h1>Purchasing Agent Console</h1>
          <p>
            An autonomous agent that investigates with tools, computes real replenishment, validates against hard constraints, executes orders, and verifies reality.
          </p>
        </div>
        <div className="page-head-actions">
          <button className="btn ghost" onClick={onReset} title="Reset database to clean initial state for scenarios">
            Reset Scenario Data
          </button>
          <button className="btn ghost" onClick={() => setShowGuide(true)}>
            Architecture & Developer Guide
          </button>
        </div>
      </header>

      <div className="split">
        <ScenarioList
          cases={cases}
          selected={selected}
          onSelect={(id) => setState({ selected: id, run: null })}
        />

        <div className="main-stage">
          {error && (
            <div className="alert" role="alert">
              ⚠️ {error}
            </div>
          )}

          {item && (
            <CaseBrief
              item={item}
              config={config}
              brain={brain}
              setBrain={setBrain}
              auto={auto}
              setAuto={setAuto}
              busy={busy}
              onRun={runAgent}
              onReset={onReset}
            />
          )}

          {!run && (
            <div className="empty-state">
              <div className="empty-icon">🎯</div>
              <h3>Ready to Evaluate Situation {selected}</h3>
              <p>
                Click <b>Run Agent Decision</b> above to watch the agent execute its 5-step lifecycle:
                <br />
                Investigate &bull; Replenish Calculation &bull; Pre-Action Sandbox Check &bull; Supplier API Call &bull; Reality Verification.
              </p>
              <button
                className="btn sm ghost"
                style={{ marginTop: '16px' }}
                onClick={() => setShowGuide(true)}
              >
                Learn How The Agent Works
              </button>
            </div>
          )}

          {run?.status === 'pending_approval' && (
            <ApprovalBanner
              run={run}
              threshold={config?.approval_threshold}
              busy={busy}
              onDecide={decide}
            />
          )}

          {run && (
            <>
              <PipelineStepper run={run} />
              <Outcome run={run} />
              <Ledger run={run} />
            </>
          )}
        </div>
      </div>
    </>
  )
}
