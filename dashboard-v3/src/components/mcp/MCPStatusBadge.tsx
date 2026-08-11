import { useEffect, useState } from 'react'
import mcpApi from './mcpApi'

export default function MCPStatusBadge({ serverId, pollInterval = 30000 }: { serverId: string; pollInterval?: number }) {
  const [status, setStatus] = useState('unknown')

  useEffect(() => {
    let cancelled = false
    const check = async () => {
      try {
        const result = await mcpApi.healthCheck(serverId)
        if (!cancelled) setStatus(result.status || 'unknown')
      } catch {
        if (!cancelled) setStatus('unhealthy')
      }
    }
    void check()
    const timer = window.setInterval(() => void check(), pollInterval)
    return () => {
      cancelled = true
      window.clearInterval(timer)
    }
  }, [serverId, pollInterval])

  const healthy = status === 'healthy' || status === 'ready'
  const authRequired = status === 'auth_required'
  const label = healthy ? 'Healthy' : authRequired ? 'Auth required' : status === 'unhealthy' ? 'Unhealthy' : 'Checking'
  const className = healthy
    ? 'border-emerald-500/25 bg-emerald-500/10 text-emerald-400'
    : authRequired
      ? 'border-amber-500/25 bg-amber-500/10 text-amber-400'
      : 'border-red-500/25 bg-red-500/10 text-red-400'

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider ${className}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {label}
    </span>
  )
}
