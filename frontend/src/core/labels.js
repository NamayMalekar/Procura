// Turns machine words from the backend into plain language. Edit wording here.
export const STATUS = {
  completed: ['Completed', 'ok'],
  completed_with_escalation: ['Completed, buyer notified', 'warn'],
  no_action: ['No purchase needed', ''],
  escalated: ['Sent to buyer', 'warn'],
  pending_approval: ['Awaiting your approval', 'warn'],
  rejected_by_human: ['Declined by you', ''],
  blocked_by_validator: ['Blocked by safety checks', 'bad'],
  escalated_after_failure: ['Escalated after failures', 'bad'],
  needs_replan: ['Needs a new plan', 'bad'],
  failed_verification: ['Failed verification', 'bad'],
}
export const DECISION = {
  accept: 'Accepted', modify: 'Modified', reject: 'Rejected', investigate: 'Needs a closer look', escalate: 'Escalated',
}
export const TOOL = {
  get_inventory: 'Inventory', get_demand: 'Demand', get_promotions: 'Promotions', get_open_pos: 'Open orders',
  get_supplier_options: 'Suppliers', get_budget: 'Budget', calculate_replenishment: 'Replenishment math',
}
export const money = (n) => `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`

export function describeAction(a) {
  if (a.action === 'create_po') return `Order ${a.qty} units from ${a.supplier_id}`
  if (a.action === 'amend_po') return `Change ${a.po_id} to ${a.qty} units`
  return `Cancel ${a.po_id}`
}
