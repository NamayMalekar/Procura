export default function Segmented({ value, onChange, options }) {
  return (
    <div className="seg" role="group">
      {options.map((o) => (
        <button key={o.value} aria-pressed={value === o.value} disabled={o.disabled} title={o.title}
          onClick={() => onChange(o.value)}>{o.label}</button>
      ))}
    </div>
  )
}
