import { useState, useMemo } from 'react'

const GROUPS = {
  0: 'All Scenarios',
  1: '1. Review a recommendation',
  2: '2. Supplier shortfall',
  3: '3. Demand surge vs spike',
  4: '4. Hard constraints & price hike',
}

const TAGS = {
  S1a: { label: 'Sound Order', tone: 'ok' },
  S1b: { label: 'Open PO Exists', tone: 'warn' },
  S1c: { label: 'Too Large (600)', tone: 'accent' },
  S1d: { label: 'Overstocked Node', tone: 'warn' },
  S2a: { label: '50% Shortfall', tone: 'bad' },
  S2b: { label: 'Enough Stock', tone: 'ok' },
  S3a: { label: 'Sustained Surge', tone: 'accent' },
  S3b: { label: '1-Day Bulk Spike', tone: 'warn' },
  S4a: { label: 'Budget Cap ($5k)', tone: 'bad' },
  S4b: { label: 'Price Rejection', tone: 'bad' },
}

export default function ScenarioList({ cases, selected, onSelect }) {
  const [filterGroup, setFilterGroup] = useState(0)
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    return cases.filter((c) => {
      const matchGroup = filterGroup === 0 || c.scenario === filterGroup
      const q = query.trim().toLowerCase()
      const matchQuery =
        !q ||
        c.id.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q) ||
        c.trigger.toLowerCase().includes(q) ||
        c.sku.toLowerCase().includes(q)
      return matchGroup && matchQuery
    })
  }, [cases, filterGroup, query])

  return (
    <nav className="scenario-nav" aria-label="Purchasing situations">
      <div className="scenario-search-box">
        <input
          type="text"
          className="search-input"
          placeholder="Filter scenarios or SKU..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {query && (
          <button className="clear-btn" onClick={() => setQuery('')} title="Clear filter">
            &times;
          </button>
        )}
      </div>

      <div className="filter-chips">
        <button
          className={`filter-chip ${filterGroup === 0 ? 'active' : ''}`}
          onClick={() => setFilterGroup(0)}
        >
          All (10)
        </button>
        <button
          className={`filter-chip ${filterGroup === 1 ? 'active' : ''}`}
          onClick={() => setFilterGroup(1)}
        >
          S1: Review (4)
        </button>
        <button
          className={`filter-chip ${filterGroup === 2 ? 'active' : ''}`}
          onClick={() => setFilterGroup(2)}
        >
          S2: Shortfall (2)
        </button>
        <button
          className={`filter-chip ${filterGroup === 3 ? 'active' : ''}`}
          onClick={() => setFilterGroup(3)}
        >
          S3: Demand (2)
        </button>
        <button
          className={`filter-chip ${filterGroup === 4 ? 'active' : ''}`}
          onClick={() => setFilterGroup(4)}
        >
          S4: Constraints (2)
        </button>
      </div>

      <div className="scenario-items-list">
        {filtered.length === 0 ? (
          <div className="empty" style={{ padding: '24px 8px' }}>
            No matching scenarios found.
          </div>
        ) : (
          filtered.map((c) => {
            const isSelected = selected === c.id
            const tag = TAGS[c.id] || { label: c.id, tone: '' }
            return (
              <button
                key={c.id}
                className={`case-card ${isSelected ? 'selected' : ''}`}
                onClick={() => onSelect(c.id)}
              >
                <div className="case-card-top">
                  <span className="case-id-badge">{c.id}</span>
                  <span className={`chip ${tag.tone}`}>{tag.label}</span>
                </div>
                <div className="case-title">{c.title}</div>
                <div className="case-trigger">{c.trigger}</div>
              </button>
            )
          })
        )}
      </div>
    </nav>
  )
}
