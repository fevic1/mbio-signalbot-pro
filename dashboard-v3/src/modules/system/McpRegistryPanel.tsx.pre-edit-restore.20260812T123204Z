import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Server, Shield, CheckCircle, XCircle, Plus, Trash2, Loader2 } from 'lucide-react'
import mcpApi from '@/components/mcp/mcpApi'
import MCPAddWizard from '@/components/mcp/MCPAddWizard'
import MCPStatusBadge from '@/components/mcp/MCPStatusBadge'

interface McpServer {
  server_id: string
  name: string
  description: string
  endpoint?: string | null
  transport?: string
  auth_type?: string
  rate_limit_per_min: number
  is_active: boolean
  status?: string
}

export function McpRegistryPanel() {
  const [servers, setServers] = useState<McpServer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showWizard, setShowWizard] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const fetchServers = async () => {
    try {
      const data = await mcpApi.listServers()
      setServers((data.servers || []) as unknown as McpServer[])
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load MCP servers')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchServers()
  }, [])

  const removeServer = async (serverId: string) => {
    if (!window.confirm(`Remove MCP server '${serverId}'?`)) return
    setDeleting(serverId)
    setError(null)
    try {
      await mcpApi.deleteServer(serverId)
      await fetchServers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove MCP server')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <Card className="rounded-2xl border-white/10 bg-white/5">
        <CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading MCP registry...
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className="rounded-2xl border-white/10 bg-white/5">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <div className="flex items-center gap-2 text-sm font-bold">
            <Server className="h-4 w-4 text-muted-foreground" />
            MCP Infrastructure Registry
          </div>
          <button
            onClick={() => setShowWizard(true)}
            className="flex items-center gap-1 rounded-md bg-emerald-600 px-3 py-1.5 text-xs text-white transition hover:bg-emerald-700"
          >
            <Plus className="h-3 w-3" /> Add MCP Server
          </button>
        </CardHeader>

        <CardContent>
          {error && <div className="mb-4 text-xs text-red-400">Error: {error}</div>}

          <div className="space-y-4">
            {servers.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">No MCP servers registered.</div>
            ) : servers.map((server) => (
              <div key={server.server_id} className="flex items-start justify-between rounded-xl border border-white/10 bg-black/20 p-4">
                <div className="min-w-0 flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-white">{server.server_id}</span>
                    {server.is_active ? <CheckCircle className="h-3.5 w-3.5 text-emerald-500" /> : <XCircle className="h-3.5 w-3.5 text-red-500" />}
                    <MCPStatusBadge serverId={server.server_id} />
                  </div>
                  <div className="text-xs text-white/50">{server.name}{server.description ? ` · ${server.description}` : ''}</div>
                  <div className="mt-2 flex flex-wrap items-center gap-4 text-[10px] uppercase tracking-wider text-muted-foreground">
                    <span className="flex items-center gap-1"><Shield className="h-3 w-3" /> Rate {server.rate_limit_per_min}/min</span>
                    <span>Transport {server.transport || 'auto'}</span>
                    <span>Auth {server.auth_type || 'none'}</span>
                    {server.endpoint && <span className="max-w-[420px] truncate normal-case">{server.endpoint}</span>}
                  </div>
                </div>
                <button
                  onClick={() => void removeServer(server.server_id)}
                  disabled={deleting === server.server_id}
                  className="ml-4 rounded p-2 text-red-400 transition hover:bg-red-500/10 hover:text-red-300 disabled:opacity-50"
                  title="Remove Server"
                >
                  {deleting === server.server_id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4" />}
                </button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {showWizard && (
        <MCPAddWizard
          onClose={() => setShowWizard(false)}
          onSuccess={async () => {
            setShowWizard(false)
            await fetchServers()
          }}
        />
      )}
    </>
  )
}
