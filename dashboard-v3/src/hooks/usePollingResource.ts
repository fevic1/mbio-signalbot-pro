import {
  DependencyList,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react"

interface PollingOptions {
  enabled?: boolean
  pauseWhenHidden?: boolean
}

export function usePollingResource<T>(
  loader: (signal?: AbortSignal) => Promise<T>,
  intervalMs: number,
  deps: DependencyList = [],
  options: PollingOptions = {},
) {
  const {
    enabled = true,
    pauseWhenHidden = true,
  } = options

  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const initialized = useRef(false)
  const running = useRef(false)
  const abortRef = useRef<AbortController | null>(null)

  const refresh = useCallback(async () => {
    if (!enabled) return
    if (running.current) return

    running.current = true

    abortRef.current?.abort()

    const controller = new AbortController()
    abortRef.current = controller

    if (!initialized.current) {
      setLoading(true)
    }

    try {
      const result = await loader(controller.signal)

      if (!controller.signal.aborted) {
        setData(result)
        setError(null)
        initialized.current = true
      }
    } catch (err) {
      if (!controller.signal.aborted) {
        setError(
          err instanceof Error
            ? err.message
            : "Unknown error"
        )
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false)
      }

      running.current = false
    }
  }, [loader, enabled])

  useEffect(() => {
    if (!enabled) return

    refresh()

    const tick = () => {
      if (pauseWhenHidden && document.hidden) {
        return
      }

      refresh()
    }

    const timer = window.setInterval(tick, intervalMs)

    const visibility = () => {
      if (!document.hidden) {
        refresh()
      }
    }

    if (pauseWhenHidden) {
      document.addEventListener(
        "visibilitychange",
        visibility
      )
    }

    return () => {
      window.clearInterval(timer)

      if (pauseWhenHidden) {
        document.removeEventListener(
          "visibilitychange",
          visibility
        )
      }

      abortRef.current?.abort()
    }
  }, [
    refresh,
    intervalMs,
    enabled,
    pauseWhenHidden,
    ...deps,
  ])

  return {
    data,
    loading,
    error,
    refresh,
    setData,
  }
}
