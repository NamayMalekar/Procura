import { useEffect, useState } from 'react'
import Button from '../../commons/Button'
import Chip from '../../commons/Chip'
import { api } from '../../core/api'
import { money } from '../../core/labels'

const TABS = [['inventory', 'Inventory'], ['purchase_orders', 'Purchase orders'], ['budgets', 'Budgets'],
  ['escalations', 'Buyer tickets'], ['audit', 'Audit log']]

const Table = ({ head, rows, empty }) => rows.length ? (
  <div className="table-wrap"><table>
    <thead><tr>{head.map(([h, r]) => <th key={h} className={r ? 'r' : ''}>{h}</th>)}</tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
) : <p className="empty">{empty}</p>

export default function DataPage({ version, onReset }) {
  const [tab, setTab] = useState('inventory')
  const [d, setD] = useState(null)
  useEffect(() => { api.state().then(setD) }, [version])
  if (!d) return <p className="empty">Loading...</p>

  const views = {
    inventory: <Table head={[['Product'], ['Node'], ['On hand', 1], ['Incoming', 1], ['Storage use']]} empty="No inventory."
      rows={d.inventory.map((r, i) => (
        <tr key={i}><td>{r.name}<div className="muted">{r.sku}</div></td><td>{r.node}</td>
          <td className="r num">{r.on_hand}</td><td className="r num">{r.incoming}</td>
          <td><div className="bar" title={`${r.on_hand + r.incoming} of ${r.capacity}`}>
            <i className="a" style={{ width: `${(r.on_hand / r.capacity) * 100}%` }} />
            <i className="b" style={{ width: `${(r.incoming / r.capacity) * 100}%` }} /></div>
            <span className="muted num">{r.on_hand + r.incoming} / {r.capacity}</span></td></tr>))} />,
    purchase_orders: <Table head={[['Order'], ['SKU'], ['Supplier'], ['Ordered', 1], ['Supplier ships', 1], ['Status'], ['Created by']]} empty="No orders."
      rows={d.purchase_orders.map((p) => (
        <tr key={p.id}><td>{p.id}</td><td>{p.sku}</td><td>{p.supplier_id}</td><td className="r num">{p.qty}</td>
          <td className="r num">{p.supplier_confirmed_qty ?? '-'}</td>
          <td><Chip tone={{ confirmed: 'ok', partial: 'warn', rejected: 'bad' }[p.status]}>{p.status}</Chip></td>
          <td>{p.created_by === 'agent' ? <Chip tone="accent">agent</Chip> : p.created_by}</td></tr>))} />,
    budgets: <Table head={[['Category'], ['Remaining', 1], ['Total', 1]]} empty="No budgets."
      rows={d.budgets.map((b) => <tr key={b.category}><td>{b.category}</td><td className="r num">{money(b.remaining)}</td><td className="r num">{money(b.total)}</td></tr>)} />,
    escalations: <Table head={[['Ticket'], ['SKU'], ['Reason'], ['Next step']]} empty="No tickets yet. The agent raises one when it needs a human."
      rows={d.escalations.map((e) => <tr key={e.id}><td>{e.id}</td><td>{e.sku}</td><td>{e.reason}</td><td>{e.follow_up}</td></tr>)} />,
    audit: <Table head={[['Event'], ['Details']]} empty="Nothing has changed yet."
      rows={d.audit.map((a, i) => { const { event, ...rest } = a; return <tr key={i}><td>{event}</td><td className="muted">{JSON.stringify(rest)}</td></tr> })} />,
  }

  return (
    <>
      <header className="page-head">
        <div><h1>System data</h1><p>What the agent sees and changes: stock, orders, budgets and tickets. Stored in a SQLite database.</p></div>
        <Button variant="ghost" onClick={onReset}>Reset to starting data</Button>
      </header>
      <div className="tabs" role="tablist">
        {TABS.map(([id, label]) => <button key={id} role="tab" aria-selected={tab === id} onClick={() => setTab(id)}>{label}</button>)}
      </div>
      {views[tab]}
    </>
  )
}
