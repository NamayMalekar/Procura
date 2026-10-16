// "Show details" toggle that reveals raw data for people who want to look under the hood.
export default function Details({ label = 'Show raw data', data }) {
  return (
    <details>
      <summary>{label}</summary>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </details>
  )
}
