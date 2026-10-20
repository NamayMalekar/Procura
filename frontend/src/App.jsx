import { useEffect, useState } from 'react'
import { api } from './core/api'
import { useTheme } from './core/theme'
import ConsolePage from './features/console/ConsolePage'
import DataPage from './features/data/DataPage'
import EvaluationPage from './features/evaluation/EvaluationPage'
import AppShell from './layout/AppShell'

export default function App() {
  const [theme, toggleTheme] = useTheme()
  const [page, setPage] = useState('console')
  const [config, setConfig] = useState(null)
  const [cases, setCases] = useState([])
  const [consoleState, setConsoleState] = useState({ selected: null, run: null })
  const [dataVersion, setDataVersion] = useState(0)          // bump to refresh the data page

  useEffect(() => {
    api.config().then(setConfig)
    api.scenarios().then((c) => { setCases(c); setConsoleState((s) => ({ ...s, selected: c[0]?.id })) })
  }, [])

  const reset = async () => { await api.reset(); setConsoleState((s) => ({ ...s, run: null })); setDataVersion((v) => v + 1) }

  return (
    <AppShell page={page} setPage={setPage} theme={theme} toggleTheme={toggleTheme} config={config}>
      {page === 'console' && (
        <ConsolePage cases={cases} config={config} state={consoleState} setState={setConsoleState}
          onDataChanged={() => setDataVersion((v) => v + 1)}
          onReset={reset} />
      )}
      {page === 'data' && <DataPage version={dataVersion} onReset={reset} />}
      {page === 'evaluation' && <EvaluationPage />}
    </AppShell>
  )
}
