export default function HowItWorksModal({ open, onClose }) {
  if (!open) return null

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span className="eyebrow" style={{ color: 'var(--accent)' }}>System Architecture</span>
            <h2 style={{ fontSize: '22px', marginTop: '4px' }}>How Procura Operates & How to Modify It</h2>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close modal">&times;</button>
        </div>

        <div className="modal-body">
          <section className="guide-section">
            <h3>1. The Closed-Loop Lifecycle (Not a Chatbot!)</h3>
            <p className="muted" style={{ marginBottom: '14px' }}>
              Unlike conversational chatbots, Procura is an autonomous execution agent that follows a verified 5-stage loop:
            </p>
            <div className="pipeline-demo">
              <div className="pipe-node active"><span className="p-num">1</span><b>Investigate</b><small>7 facts gathered</small></div>
              <div className="pipe-arrow">&rarr;</div>
              <div className="pipe-node active"><span className="p-num">2</span><b>Calculate</b><small>Replenish math</small></div>
              <div className="pipe-arrow">&rarr;</div>
              <div className="pipe-node active"><span className="p-num">3</span><b>Sandbox Check</b><small>In-memory DB test</small></div>
              <div className="pipe-arrow">&rarr;</div>
              <div className="pipe-node active"><span className="p-num">4</span><b>Execute</b><small>Supplier API call</small></div>
              <div className="pipe-arrow">&rarr;</div>
              <div className="pipe-node active"><span className="p-num">5</span><b>Verify</b><small>Reality check & replan</small></div>
            </div>
          </section>

          <section className="guide-section" style={{ marginTop: '24px' }}>
            <h3>2. The Two Feedback Loops</h3>
            <div className="two-cols-guide">
              <div className="guide-card">
                <span className="chip ok" style={{ marginBottom: '8px' }}>Loop 1: Pre-Action Sandbox</span>
                <p>
                  Before sending an order to a supplier, <code>validator.py</code> clones the database in memory and tests:
                  Budget, Storage, 125% Stock Ceiling, MOQ, and Supplier Reliability (&ge; 0.75).
                  If violated, the brain gets up to 3 tries to fix it.
                </p>
              </div>
              <div className="guide-card">
                <span className="chip accent" style={{ marginBottom: '8px' }}>Loop 2: Post-Action Reality Check</span>
                <p>
                  After execution, the real database is compared with the planned position.
                  If a supplier rejected the order (e.g., stale price in <b>S4b</b>) or only partially shipped (<b>S2a</b>),
                  Cycle 2 replans automatically or files a human buyer ticket.
                </p>
              </div>
            </div>
          </section>

          <section className="guide-section" style={{ marginTop: '24px' }}>
            <h3>3. Developer Cheat Sheet: Where to Make Changes</h3>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>To change...</th>
                    <th>Edit this file</th>
                    <th>What it does</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><b>Approval limit ($10k) or Cover factor</b></td>
                    <td><code>backend/app/core/policy.py</code></td>
                    <td>Change whiteboard rules: approval threshold, max cover, min reliability</td>
                  </tr>
                  <tr>
                    <td><b>Decision logic & Playbook</b></td>
                    <td><code>backend/app/agent/brains/rules.py</code></td>
                    <td>Change how the agent evaluates suppliers, calculates pack sizes, and prioritizes</td>
                  </tr>
                  <tr>
                    <td><b>Pre-Action Safety Rules</b></td>
                    <td><code>backend/app/agent/validator.py</code></td>
                    <td>Add new hard constraints that prevent orders from reaching suppliers</td>
                  </tr>
                  <tr>
                    <td><b>Add a New Scenario</b></td>
                    <td><code>backend/app/evaluation/cases.py</code></td>
                    <td>Define new business situations (SKU, trigger, suggested quantity)</td>
                  </tr>
                  <tr>
                    <td><b>UI Appearance & Tokens</b></td>
                    <td><code>frontend/src/styles/tokens.css</code></td>
                    <td>Adjust colors, typography, border radius, and dark mode tokens</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="muted" style={{ marginTop: '12px', fontSize: '13px' }}>
              Full documentation with code diagrams is available in <code>DEVELOPER_GUIDE.md</code> at the project root.
            </p>
          </section>
        </div>

        <div className="modal-footer">
          <button className="btn" onClick={onClose}>Got it, close guide</button>
        </div>
      </div>
    </div>
  )
}
