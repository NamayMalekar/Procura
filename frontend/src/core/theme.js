import { useEffect, useState } from 'react'

// Remembers light/dark in the browser and follows the system setting the first time.
export function useTheme() {
  const [theme, setTheme] = useState(
    () => localStorage.getItem('procura-theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'),
  )
  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('procura-theme', theme)
  }, [theme])
  return [theme, () => setTheme(theme === 'dark' ? 'light' : 'dark')]
}
