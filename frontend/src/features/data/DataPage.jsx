import { useEffect, useState, useMemo } from 'react'
import Button from '../../commons/Button'
import Chip from '../../commons/Chip'
import { api } from '../../core/api'
import { money } from '../../core/labels'

const TABS = [
  ['inventory', 'Inventory Position'],
  ['purchase_orders', 'Purchase Orders'],
  ['budgets', 'Category Budgets'],
  ['escalations', 'Buyer Tickets'],
  ['audit', 'Audit Log Trail'],
]

const Table = ({ head, rows, empty }) =>
  rows.length ? (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {head.map(([h, r]) => (
              <th key={h} className={r ? 'r' : ''}>
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>
  ) : (
    <div className="empty-state" style={{ padding: '36px' }}>
      <p className="empty">{empty}</p>
    </div>
  )

export default function DataPage({ version, onReset }) {
  const [tab, setTab] = useState('inventory')
  const [d, setD] = useState(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    api.state().then(setD)
  }, [version])

  const q = query.trim().toLowerCase()

  const filteredInventory = useMemo(() => {
    if (!d?.inventory) return []
    if (!q) return d.inventory
    return d.inventory.filter(
      (r) =>
        r.name.toLowerCase().includes(q) ||
        r.sku.toLowerCase().includes(q) ||
        r.node.toLowerCase().includes(q)
    )
  }, [d, q])

  const filteredOrders = useMemo(() => {
    if (!d?.purchase_orders) return []
    if (!q) return d.purchase_orders
    return d.purchase_orders.filter(
      (p) =>
        p.id.toLowerCase().includes(q) ||
        p.sku.toLowerCase().includes(q) ||
        p.supplier_id.toLowerCase().includes(q) ||
        p.status.toLowerCase().includes(q)
    )
  }, [d, q])

  if (!d) return <p className="empty" style={{ padding: '60px' }}>Loading system state from SQLite...</p>

  const totalOrders = d.purchase_orders.length
  const agentOrders = d.purchase_orders.filter((p) => p.created_by === 'agent').length
  const totalRemainingBudget = d.budgets.reduce((acc, b) => acc + (b.remaining || 0), 0)
  const openEscalations = d.escalations.length

  const views = {
    inventory: (
      <Table
        head={[['Product'], ['Node'], ['On hand', 1], ['Inbound PO', 1], ['Storage Capacity Fill']]}
        empty="No inventory records found."
        rows={filteredInventory.map((r, i) => (
          <tr key={i}>
            <td>
              <b>{r.name}</b>
              <div className="muted">{r.sku}</div>
            </td>
            <td>
              <span className="chip">{r.node}</span>
            </td>
            <td className="r num">
              <b>{r.on_hand}</b>
            </td>
            <td className="r num">
              <span style={{ color: r.incoming > 0 ? 'var(--accent)' : 'var(--muted)' }}>
                {r.incoming > 0 ? `+${r.incoming}` : '0'}
              </span>
            </td>
            <td>
              <div className="bar" title={`${r.on_hand + r.incoming} of ${r.capacity} units`}>
                <i className="a" style={{ width: `${Math.min(100, (r.on_hand / r.capacity) * 100)}%` }} />
                <i className="b" style={{ width: `${Math.min(100, (r.incoming / r.capacity) * 100)}%` }} />
              </div>
              <span className="muted num" style={{ fontSize: '12px', marginTop: '2px', display: 'block' }}>
                {r.on_hand + r.incoming} / {r.capacity} units (
                {Math.round(((r.on_hand + r.incoming) / r.capacity) * 100)}%)
              </span>
            </td>
          </tr>
        ))}
      />
    ),

    purchase_orders: (
      <Table
        head={[['Order ID'], ['SKU'], ['Supplier'], ['Ordered', 1], ['Confirmed', 1], ['Status'], ['Created By']]}
        empty="No purchase orders found."
        rows={filteredOrders.map((p) => (
          <tr key={p.id}>
            <td>
              <b>{p.id}</b>
            </td>
            <td>
              <span className="chip">{p.sku}</span>
            </td>
            <td>{p.supplier_id}</td>
            <td className="r num">
              <b>{p.qty}</b>
            </td>
            <td className="r num">
              {p.supplier_confirmed_qty !== null ? (
                <span className={p.supplier_confirmed_qty < p.qty ? 'num warn' : 'num'}>
                  {p.supplier_confirmed_qty}
                </span>
              ) : (
                '-'
              )}
            </td>
            <td>
              <Chip tone={{ confirmed: 'ok', partial: 'warn', rejected: 'bad' }[p.status]}>
                {p.status.toUpperCase()}
              </Chip>
            </td>
            <td>
              {p.created_by === 'agent' ? (
                <Chip tone="accent">AI Agent</Chip>
              ) : (
                <Chip>{p.created_by}</Chip>
              )}
            </td>
          </tr>
        ))}
      />
    ),

    budgets: (
      <Table
        head={[['Category'], ['Remaining Budget', 1], ['Total Allocated', 1], ['Utilization']]}
        empty="No category budgets found."
        rows={d.budgets.map((b) => {
          const used = b.total - b.remaining
          const pct = Math.round((used / b.total) * 100)
          return (
            <tr key={b.category}>
              <td>
                <b>{b.category}</b>
              </td>
              <td className="r num">
                <b style={{ color: b.remaining < 2000 ? 'var(--warn)' : 'var(--ok)' }}>
                  {money(b.remaining)}
                </b>
              </td>
              <td className="r num">{money(b.total)}</td>
              <td>
                <div className="bar" style={{ width: '160px' }}>
                  <i className="a" style={{ width: `${pct}%`, background: 'var(--accent)' }} />
                </div>
                <span className="muted num" style={{ fontSize: '12px' }}>
                  {pct}% spent ({money(used)})
                </span>
              </td>
            </tr>
          )
        })}
      />
    ),

    escalations: (
      <Table
        head={[['Ticket ID'], ['SKU'], ['Escalation Reason'], ['Recommended Next Step']]}
        empty="No active buyer tickets. The agent raises one automatically when a human decision is required."
        rows={d.escalations.map((e) => (
          <tr key={e.id}>
            <td>
              <span className="chip bad">Ticket {e.id}</span>
            </td>
            <td>
              <span className="chip">{e.sku}</span>
            </td>
            <td>
              <b>{e.reason}</b>
            </td>
            <td className="muted">{e.follow_up}</td>
          </tr>
        ))}
      />
    ),

    audit: (
      <div className="audit-timeline">
        {d.audit.length === 0 ? (
          <p className="empty">No audit events recorded yet.</p>
        ) : (
          d.audit.map((a, i) => {
            const { event, ...rest } = a
            return (
              <div key={i} className="audit-card">
                <div className="audit-card-head">
                  <span className="chip accent">{event}</span>
                  <span className="muted" style={{ fontSize: '12px' }}>Event #{d.audit.length - i}</span>
                </div>
                <div className="audit-card-body">
                  <pre>{JSON.stringify(rest, null, 2)}</pre>
                </div>
              </div>
            )
          })
        )}
      </div>
    ),
  }

  return (
    <>
      <header className="page-head">
        <div>
          <div className="eyebrow" style={{ color: 'var(--accent)' }}>System Persistence</div>
          <h1>System Data & Live Database</h1>
          <p>
            Real-time state inspected and modified by the agent: inventory levels, purchase orders, category budgets, and audit logs.
          </p>
        </div>
        <Button variant="ghost" onClick={onReset}>
          ↺ Reset to Starting Demo State
        </Button>
      </header>

      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <span className="stat-label">Total Inventory Items</span>
          <div className="stat-value num">{d.inventory.length}</div>
          <span className="stat-desc">Across all dark stores</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total Purchase Orders</span>
          <div className="stat-value num">{totalOrders}</div>
          <span className="stat-desc">{agentOrders} created by AI Agent</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Remaining Budget</span>
          <div className="stat-value num" style={{ color: 'var(--ok)' }}>
            {money(totalRemainingBudget)}
          </div>
          <span className="stat-desc">Across categories</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Active Buyer Tickets</span>
          <div className="stat-value num" style={{ color: openEscalations > 0 ? 'var(--warn)' : 'var(--muted)' }}>
            {openEscalations}
          </div>
          <span className="stat-desc">Awaiting human review</span>
        </div>
      </div>

      <div className="data-toolbar">
        <div className="tabs" role="tablist" style={{ marginBottom: 0 }}>
          {TABS.map(([id, label]) => (
            <button
              key={id}
              role="tab"
              aria-selected={tab === id}
              onClick={() => {
                setTab(id)
                setQuery('')
              }}
            >
              {label}
            </button>
          ))}
        </div>
        {(tab === 'inventory' || tab === 'purchase_orders') && (
          <input
            type="text"
            className="search-input"
            style={{ maxWidth: '280px' }}
            placeholder={`Search ${tab}...`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        )}
      </div>

      {views[tab]}
    </>
  )
}
