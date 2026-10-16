const GROUPS = {
  1: 'Review a recommendation',
  2: 'Supplier cannot fulfil',
  3: 'Demand has changed',
  4: 'A constraint blocks the buy',
}

export default function ScenarioList({ cases, selected, onSelect }) {
  return (
    <nav aria-label="Purchasing situations">
      {Object.entries(GROUPS).map(([n, title]) => (
        <section key={n}>
          <div className="eyebrow group-title">Scenario {n} &nbsp;{title}</div>
          {cases.filter((c) => c.scenario === Number(n)).map((c) => (
            <button key={c.id} className="case" aria-current={selected === c.id} onClick={() => onSelect(c.id)}>
              <b>{c.title}</b>
              <span>{c.trigger}</span>
            </button>
          ))}
        </section>
      ))}
    </nav>
  )
}
