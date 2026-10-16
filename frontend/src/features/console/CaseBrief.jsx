import Button from '../../commons/Button'
import Chip from '../../commons/Chip'
import Icon from '../../commons/Icon'
import Segmented from '../../commons/Segmented'
import Switch from '../../commons/Switch'

export default function CaseBrief({ item, config, brain, setBrain, auto, setAuto, busy, onRun }) {
  return (
    <div className="card brief">
      <div className="eyebrow">Situation {item.id}</div>
      <h2>{item.title}</h2>
      <p className="muted">{item.trigger}</p>
      <div className="meta">
        <Chip>{item.sku}</Chip>
        <Chip>{item.node}</Chip>
        {item.recommended_qty && <Chip tone="accent">System suggests {item.recommended_qty} units</Chip>}
      </div>
      <div className="controls">
        <Segmented value={brain} onChange={setBrain} options={[
          { value: 'rules', label: 'Built-in rules' },
          { value: 'llm', label: 'Claude', disabled: !config?.llm_available, title: config?.llm_available ? '' : 'Add ANTHROPIC_API_KEY to backend/.env' },
        ]} />
        <Switch checked={auto} onChange={setAuto} label="Skip human approval" />
        <span className="grow" />
        <Button onClick={onRun} disabled={busy}><Icon name="play" size={14} /> {busy ? 'Agent is working...' : 'Run agent'}</Button>
      </div>
    </div>
  )
}
