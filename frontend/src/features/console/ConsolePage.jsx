import { useState } from 'react'
import { api } from '../../core/api'
import ApprovalBanner from './ApprovalBanner'
import CaseBrief from './CaseBrief'
import Ledger from './Ledger'
import Outcome from './Outcome'
import ScenarioList from './ScenarioList'

export default function ConsolePage({ cases, config, state, setState, onDataChanged }) {
  const { selected, run } = state
  const [brain, setBrain] = useState('rules')
  const [auto, setAuto] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const item = cases.find((c) => c.id === selected)

  const guard = async (fn) => {
    setBusy(true); setError('')
    try { await fn(); onDataChanged() } catch (e) { setError(e.message) } finally { setBusy(false) }
  }
  const runAgent = () => guard(async () => setState({ selected, run: await api.startRun({ case_id: selected, brain, auto_approve: auto }) }))
  const decide = (ok) => guard(async () => setState({ selected, run: await api.decide(run.run_id, ok) }))

  return (
    <>
      <header className="page-head">
        <div>
          <h1>Agent console</h1>
          <p>Choose a purchasing situation. The agent investigates, decides, acts, then checks its own result.</p>
        </div>
      </header>
      <div className="split">
        <ScenarioList cases={cases} selected={selected} onSelect={(id) => setState({ selected: id, run: null })} />
        <div>
          {error && <div className="alert" role="alert">{error}</div>}
          {item && <CaseBrief item={item} config={config} brain={brain} setBrain={setBrain} auto={auto} setAuto={setAuto} busy={busy} onRun={runAgent} />}
          {!run && (
            <div className="empty-state">
              <h3>Ready when you are</h3>
              <p>Press Run agent to watch it work through this situation step by step.<br />
                Each run changes the system data. Reset it any time from System data.</p>
            </div>
          )}
          {run?.status === 'pending_approval' && <ApprovalBanner run={run} threshold={config?.approval_threshold} busy={busy} onDecide={decide} />}
          {run && <><Outcome run={run} /><Ledger run={run} /></>}
        </div>
      </div>
    </>
  )
}
