import { DependencyList, useCallback, useEffect, useState } from "react"

export function usePollingResource<T>(
  loader: () => Promise<T>,
  intervalMs: number,
  deps: DependencyList = []
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      const result = await loader()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
    } finally {
      setLoading(false)
    }
  }, [loader])

  useEffect(() => {
    refresh()
    const id = window.setInterval(refresh, intervalMs)
    return () => window.clearInterval(id)
  }, [refresh, intervalMs, ...deps])

  return {
    data,
    loading,
    error,
    refresh,
    setData,
  }
}
