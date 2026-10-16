export default function Chip({ tone = '', children }) {
  return <span className={`chip ${tone}`}>{children}</span>
}
