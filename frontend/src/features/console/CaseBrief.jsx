import Button from '../../commons/Button'
import Chip from '../../commons/Chip'
import Icon from '../../commons/Icon'
import Segmented from '../../commons/Segmented'
import Switch from '../../commons/Switch'

export default function CaseBrief({ item, config, brain, setBrain, auto, setAuto, busy, onRun, onReset }) {
  return (
    <div className="card brief">
      <div className="brief-top">
        <div>
          <div className="eyebrow" style={{ color: 'var(--accent)' }}>Purchasing Situation {item.id}</div>
          <h2>{item.title}</h2>
        </div>
        <div className="brief-badges">
          <span className="chip accent">SKU: {item.sku}</span>
          <span className="chip">Node: {item.node}</span>
        </div>
      </div>

      <div className="brief-highlight">
        <div className="trigger-icon">⚡</div>
        <div className="trigger-text">
          <b>Trigger Event:</b> {item.trigger}
        </div>
      </div>

      <div className="brief-meta-grid">
        <div className="meta-card">
          <span className="eyebrow">Catalog SKU</span>
          <b>{item.sku}</b>
        </div>
        <div className="meta-card">
          <span className="eyebrow">Fulfillment Node</span>
          <b>{item.node}</b>
        </div>
        <div className="meta-card">
          <span className="eyebrow">Trigger Recommendation</span>
          <b style={{ color: item.recommended_qty ? 'var(--accent)' : 'var(--muted)' }}>
            {item.recommended_qty ? `${item.recommended_qty} units` : 'N/A (Shortfall Alert)'}
          </b>
        </div>
        <div className="meta-card">
          <span className="eyebrow">Agent Task</span>
          <b>Investigate & Validate</b>
        </div>
      </div>

      <div className="controls">
        <div className="control-group">
          <span className="eyebrow" style={{ display: 'block', marginBottom: '6px' }}>Decision Engine</span>
          <Segmented
            value={brain}
            onChange={setBrain}
            options={[
              { value: 'rules', label: 'Built-in Rules (Offline)' },
              {
                value: 'llm',
                label: 'Claude Sonnet',
                disabled: !config?.llm_available,
                title: config?.llm_available ? '' : 'Add ANTHROPIC_API_KEY to .env to enable',
              },
            ]}
          />
        </div>

        <div className="control-group">
          <span className="eyebrow" style={{ display: 'block', marginBottom: '6px' }}>Execution Mode</span>
          <Switch checked={auto} onChange={setAuto} label="Skip human approval" />
        </div>

        <span className="grow" />

        {onReset && (
          <button
            type="button"
            className="btn ghost"
            onClick={onReset}
            disabled={busy}
            title="Reset database to clean initial state for this scenario"
            style={{ marginRight: '8px' }}
          >
            Reset Data
          </button>
        )}

        <Button onClick={onRun} disabled={busy} className="run-agent-btn">
          <Icon name="play" size={16} />
          {busy ? 'Agent Investigating & Executing...' : 'Run Agent Decision'}
        </Button>
      </div>
    </div>
  )
}
