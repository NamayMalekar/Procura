import Icon from '../commons/Icon'

const NAV = [
  ['console', 'Agent console', 'console'],
  ['data', 'System data', 'data'],
  ['evaluation', 'Evaluation', 'check'],
]

export default function AppShell({ page, setPage, theme, toggleTheme, config, children }) {
  return (
    <div className="shell">
      <aside className="side">
        <div className="brand">
          <span className="brand-mark">P</span>
          <div>
            <b>Procura</b>
            <small>AI PURCHASING AGENT</small>
          </div>
        </div>
        <nav className="nav" aria-label="Main">
          {NAV.map(([id, label, icon]) => (
            <button key={id} aria-current={page === id ? 'page' : undefined} onClick={() => setPage(id)}>
              <Icon name={icon} /> {label}
            </button>
          ))}
        </nav>
        <div className="side-foot">
          <div className="engine">
            Engine: {config?.llm_available ? `Claude or built-in rules` : 'Built-in rules (offline)'}
            <br />Approval needed above ${config?.approval_threshold?.toLocaleString() ?? '10,000'}
          </div>
          <button onClick={toggleTheme}>
            <Icon name={theme === 'dark' ? 'sun' : 'moon'} size={16} /> {theme === 'dark' ? 'Light mode' : 'Dark mode'}
          </button>
        </div>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}
