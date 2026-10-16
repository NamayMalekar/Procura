// All calls to the backend live here. Components never use fetch directly.
async function request(path, options) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
    body: options?.body ? JSON.stringify(options.body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`)
  return data
}

export const api = {
  config: () => request('/config'),
  scenarios: () => request('/scenarios'),
  state: () => request('/state'),
  reset: () => request('/system/reset', { method: 'POST' }),
  startRun: (body) => request('/runs', { method: 'POST', body }),
  decide: (runId, approve) => request(`/runs/${runId}/approval`, { method: 'POST', body: { approve } }),
  evaluation: () => request('/evaluation'),
}
