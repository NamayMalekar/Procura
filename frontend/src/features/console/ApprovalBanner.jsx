import Button from '../../commons/Button'
import { money } from '../../core/labels'

export default function ApprovalBanner({ run, threshold, busy, onDecide }) {
  const cost = run.pending?.verdict?.total_cost ?? 0
  return (
    <div className="approve">
      <div className="grow">
        <h3>Your approval is needed</h3>
        <p className="muted">This order is worth {money(cost)}, above the {money(threshold)} limit. The agent will re-check everything before placing it.</p>
      </div>
      <div className="btns">
        <Button variant="ghost" disabled={busy} onClick={() => onDecide(false)}>Decline</Button>
        <Button disabled={busy} onClick={() => onDecide(true)}>Approve and place order</Button>
      </div>
    </div>
  )
}
