import { useCallback, useRef, useState } from 'react'
import mcpApi from './mcpApi'

export const STEPS = {
  IDLE: 'idle',
  VALIDATE: 'validate',
  TRANSPORT: 'transport',
  CONNECT: 'connect',
  AUTHENTICATE: 'authenticate',
  DISCOVER: 'discover',
  HEALTH: 'health',
  READY: 'ready',
  ERROR: 'error',
} as const

export function useMCPFlow() {
  const [step, setStep] = useState<string>(STEPS.IDLE)
  const [error, setError] = useState<string | null>(null)
  const [serverId, setServerId] = useState<string | null>(null)
  const [discoveredTools, setDiscoveredTools] =
    useState<Array<Record<string, unknown>>>([])
  const [healthStatus, setHealthStatus] =
    useState<Record<string, unknown> | null>(null)
  const [logs, setLogs] = useState<Array<{
    time: string
    message: string
  }>>([])
  const abortRef = useRef(false)

  const log = useCallback((message: string) => {
    setLogs((prev) => [
      ...prev,
      {
        time: new Date().toISOString(),
        message,
      },
    ])
  }, [])

  const reset = useCallback(() => {
    abortRef.current = false
    setStep(STEPS.IDLE)
    setError(null)
    setServerId(null)
    setDiscoveredTools([])
    setHealthStatus(null)
    setLogs([])
  }, [])

  const cancel = useCallback(() => {
    abortRef.current = true
    log('Flow cancelled by user')
    setStep(STEPS.IDLE)
  }, [log])

  const runFlow = useCallback(async (
    config: Record<string, unknown>,
  ) => {
    reset()

    const checkAbort = () => {
      if (abortRef.current) {
        throw new Error('CANCELLED')
      }
    }

    try {
      setStep(STEPS.VALIDATE)
      log('Validating MCP configuration...')

      const validation = await mcpApi.validateConfig(config)
      checkAbort()

      if (!validation.valid) {
        throw new Error(
          validation.error ||
          'Configuration validation failed',
        )
      }

      setStep(STEPS.TRANSPORT)
      log('Detecting MCP transport...')

      const detected = await mcpApi.detectTransport(config)
      checkAbort()

      const transport =
        detected.transport ||
        String(config.transport || 'streamable_http')

      config.transport = transport
      log(`Transport: ${transport}`)

      setStep(STEPS.CONNECT)
      log('Connecting to MCP server...')

      const result = await mcpApi.connect(config)
      checkAbort()

      if (result.status === 'auth_required') {
        setStep(STEPS.AUTHENTICATE)
        log('MCP server requires OAuth authentication.')

        if (!result.transaction_id ||
            !result.authorization_url) {
          throw new Error(
            'MCP requested authentication but no OAuth authorization URL was returned.',
          )
        }

        log('Opening OAuth authorization...')

        window.open(
          result.authorization_url,
          '_blank',
          'noopener,noreferrer',
        )

        for (;;) {
          await new Promise((resolve) => setTimeout(resolve, 1000))
          checkAbort()

          const status = await mcpApi.oauthStatus(
            result.transaction_id,
          )

          if (status.status === 'ready') {
            setServerId(status.server_id || null)
            setDiscoveredTools(status.tools || [])
            setHealthStatus(status.health || null)
            break
          }

          if (
            status.status === 'error' ||
            status.status === 'cancelled'
          ) {
            throw new Error(
              status.error ||
              `OAuth flow ended with status ${status.status}`,
            )
          }
        }

      } else if (result.status === 'ready') {
        setServerId(result.server_id || null)
        setDiscoveredTools(result.tools || [])
        setHealthStatus(result.health || null)
      } else {
        throw new Error(
          result.error ||
          'MCP connection failed',
        )
      }

      setStep(STEPS.DISCOVER)
      log(`Discovered ${discoveredTools.length || 0} tool(s)`)

      setStep(STEPS.HEALTH)
      log('MCP connection healthy')

      setStep(STEPS.READY)
      log('MCP server ready')

      return {
        serverId: result.server_id || serverId,
        tools: result.tools || discoveredTools,
        health: result.health || healthStatus,
      }

    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : String(err)

      if (message === 'CANCELLED') {
        log('Flow aborted')
        return null
      }

      setError(message)
      setStep(STEPS.ERROR)
      log(`ERROR: ${message}`)
      throw err
    }
  }, [
    discoveredTools,
    healthStatus,
    log,
    reset,
    serverId,
  ])

  return {
    step,
    error,
    serverId,
    discoveredTools,
    healthStatus,
    logs,
    runFlow,
    reset,
    cancel,
    isRunning: ![
      STEPS.IDLE,
      STEPS.READY,
      STEPS.ERROR,
    ].includes(step as never),
    isReady: step === STEPS.READY,
    hasError: step === STEPS.ERROR,
  }
}

export default useMCPFlow
