import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
  Server,
  Shield,
  CheckCircle,
  XCircle,
  Plus,
  Trash2,
  Loader2,
  Pencil,
  X,
} from 'lucide-react'
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
  auth_header?: string
  rate_limit_per_min: number
  is_active: boolean
  enabled?: boolean
  status?: string
}

interface McpEditForm {
  server_id: string
  name: string
  description: string
  endpoint: string
  transport: string
  auth_type: string
  api_key: string
  auth_token: string
  auth_header: string
  rate_limit_per_min: number
  enabled: boolean
}

const emptyEditForm: McpEditForm = {
  server_id: '',
  name: '',
  description: '',
  endpoint: '',
  transport: 'auto',
  auth_type: 'none',
  api_key: '',
  auth_token: '',
  auth_header: 'X-API-Key',
  rate_limit_per_min: 60,
  enabled: true,
}

export function McpRegistryPanel() {
  const [servers, setServers] = useState<McpServer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showWizard, setShowWizard] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [editing, setEditing] = useState<McpServer | null>(null)
  const [editForm, setEditForm] = useState<McpEditForm>(emptyEditForm)
  const [saving, setSaving] = useState(false)

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

  const openEdit = (server: McpServer) => {
    setError(null)
    setEditing(server)
    setEditForm({
      server_id: server.server_id,
      name: server.name || '',
      description: server.description || '',
      endpoint: server.endpoint || '',
      transport: server.transport || 'auto',
      auth_type: server.auth_type || 'none',
      api_key: '',
      auth_token: '',
      auth_header: server.auth_header || 'X-API-Key',
      rate_limit_per_min: Number(server.rate_limit_per_min || 60),
      enabled: server.enabled ?? server.is_active ?? true,
    })
  }

  const closeEdit = () => {
    if (saving) return
    setEditing(null)
    setEditForm(emptyEditForm)
  }

  const saveEdit = async (event: React.FormEvent) => {
    event.preventDefault()

    if (!editing) return

    setSaving(true)
    setError(null)

    try {
      const payload: Record<string, unknown> = {
        server_id: editForm.server_id,
        name: editForm.name.trim(),
        description: editForm.description.trim(),
        endpoint: editForm.endpoint.trim(),
        transport: editForm.transport,
        auth_type: editForm.auth_type,
        auth_header: editForm.auth_header.trim() || 'X-API-Key',
        rate_limit_per_min: Number(editForm.rate_limit_per_min),
        enabled: Boolean(editForm.enabled),
      }

      // Blank credentials intentionally mean:
      // preserve the existing credential in the backend registry.
      if (editForm.api_key.trim()) {
        payload.api_key = editForm.api_key.trim()
      }

      if (editForm.auth_token.trim()) {
        payload.auth_token = editForm.auth_token.trim()
      }

      await mcpApi.updateServer(editing.server_id, payload)

      setEditing(null)
      setEditForm(emptyEditForm)
      await fetchServers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update MCP server')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Card className="rounded-2xl border-white/10 bg-white/5">
        <CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading MCP registry...
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
            <Plus className="h-3 w-3" />
            Add MCP Server
          </button>
        </CardHeader>

        <CardContent>
          {error && (
            <div className="mb-4 rounded border border-red-500/20 bg-red-500/5 p-3 text-xs text-red-400">
              Error: {error}
            </div>
          )}

          <div className="space-y-4">
            {servers.length === 0 ? (
              <div className="py-6 text-center text-sm text-muted-foreground">
                No MCP servers registered.
              </div>
            ) : (
              servers.map((server) => (
                <div
                  key={server.server_id}
                  className="group flex items-start justify-between rounded-xl border border-white/10 bg-black/20 p-4"
                >
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex items-center gap-2">
                      <span className="font-mono text-sm font-bold text-white">
                        {server.server_id}
                      </span>

                      {server.is_active ? (
                        <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                      ) : (
                        <XCircle className="h-3.5 w-3.5 text-red-500" />
                      )}

                      <MCPStatusBadge serverId={server.server_id} />
                    </div>

                    <div className="text-xs text-white/50">
                      {server.name}
                      {server.description ? ` · ${server.description}` : ''}
                    </div>

                    <div className="mt-2 flex flex-wrap items-center gap-4 text-[10px] uppercase tracking-wider text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Shield className="h-3 w-3" />
                        Rate {server.rate_limit_per_min}/min
                      </span>

                      <span>Transport {server.transport || 'auto'}</span>
                      <span>Auth {server.auth_type || 'none'}</span>

                      {server.endpoint && (
                        <span className="max-w-[420px] truncate normal-case">
                          {server.endpoint}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="ml-4 flex items-center gap-1">
                    <button
                      onClick={() => openEdit(server)}
                      className="rounded p-2 text-muted-foreground transition hover:bg-white/10 hover:text-white"
                      title="Edit Server"
                      aria-label={`Edit ${server.server_id}`}
                    >
                      <Pencil className="h-4 w-4" />
                    </button>

                    <button
                      onClick={() => void removeServer(server.server_id)}
                      disabled={deleting === server.server_id}
                      className="rounded p-2 text-red-400 transition hover:bg-red-500/10 hover:text-red-300 disabled:opacity-50"
                      title="Remove Server"
                      aria-label={`Remove ${server.server_id}`}
                    >
                      {deleting === server.server_id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
              ))
            )}
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

      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border border-white/10 bg-background shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <div>
                <h2 className="text-sm font-bold">Edit MCP Server</h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  Update connection and server details.
                </p>
              </div>

              <button
                type="button"
                onClick={closeEdit}
                disabled={saving}
                className="rounded p-2 text-muted-foreground transition hover:bg-white/10 hover:text-white disabled:opacity-50"
                title="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <form onSubmit={saveEdit} className="space-y-4 p-5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="mb-1 block text-[11px] text-muted-foreground">
                    Server ID
                  </label>
                  <input
                    value={editForm.server_id}
                    disabled
                    className="w-full rounded border border-border bg-muted/20 px-3 py-2 text-sm text-muted-foreground"
                  />
                </div>

                <div>
                  <label className="mb-1 block text-[11px] text-muted-foreground">
                    Display name
                  </label>
                  <input
                    required
                    value={editForm.name}
                    onChange={(e) =>
                      setEditForm({ ...editForm, name: e.target.value })
                    }
                    className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
                  />
                </div>

                <div className="col-span-2">
                  <label className="mb-1 block text-[11px] text-muted-foreground">
                    MCP endpoint
                  </label>
                  <input
                    required
                    value={editForm.endpoint}
                    onChange={(e) =>
                      setEditForm({ ...editForm, endpoint: e.target.value })
                    }
                    className="w-full rounded border border-border bg-background px-3 py-2 text-sm"
                  />
                </div>

                <div className="col-span-2">
                  <label className="mb-1 block text-[11px] text-muted-foreground">
                    Description
                  </label>
                  <textarea
                    value={editForm.description}
                    rows={3}
                    onChange={(e) =>
                      setEditForm({ ...editForm, description: e.target.value })
                    }
                    className="w-full resize-y rounded border border-border bg-background px-3 py-2 text-sm"
                  />
                </div>

                <select
                  value={editForm.transport}
                  onChange={(e) =>
                    setEditForm({ ...editForm, transport: e.target.value })
                  }
                  className="rounded border border-border bg-background px-3 py-2 text-sm"
                >
                  <option value="auto">Auto-detect transport</option>
                  <option value="streamable_http">Streamable HTTP</option>
                  <option value="sse">SSE (legacy)</option>
                </select>

                <select
                  value={editForm.auth_type}
                  onChange={(e) =>
                    setEditForm({ ...editForm, auth_type: e.target.value })
                  }
                  className="rounded border border-border bg-background px-3 py-2 text-sm"
                >
                  <option value="none">No authentication</option>
                  <option value="api_key">API key</option>
                  <option value="bearer">Bearer token</option>
                  <option value="oauth">OAuth access token</option>
                </select>

                {editForm.auth_type === 'api_key' && (
                  <>
                    <input
                      type="password"
                      placeholder="Paste new API key (blank = keep existing)"
                      value={editForm.api_key}
                      onChange={(e) =>
                        setEditForm({ ...editForm, api_key: e.target.value })
                      }
                      className="rounded border border-border bg-background px-3 py-2 text-sm"
                      autoComplete="off"
                    />

                    <input
                      placeholder="Header name"
                      value={editForm.auth_header}
                      onChange={(e) =>
                        setEditForm({
                          ...editForm,
                          auth_header: e.target.value,
                        })
                      }
                      className="rounded border border-border bg-background px-3 py-2 text-sm"
                    />
                  </>
                )}

                {['bearer', 'oauth'].includes(editForm.auth_type) && (
                  <input
                    type="password"
                    placeholder="Paste new access token (blank = keep existing)"
                    value={editForm.auth_token}
                    onChange={(e) =>
                      setEditForm({
                        ...editForm,
                        auth_token: e.target.value,
                      })
                    }
                    className="col-span-2 rounded border border-border bg-background px-3 py-2 text-sm"
                    autoComplete="off"
                  />
                )}

                <input
                  type="number"
                  min={1}
                  value={editForm.rate_limit_per_min}
                  onChange={(e) =>
                    setEditForm({
                      ...editForm,
                      rate_limit_per_min: Number(e.target.value),
                    })
                  }
                  className="rounded border border-border bg-background px-3 py-2 text-sm"
                />

                <label className="flex items-center gap-2 rounded border border-border bg-background px-3 py-2 text-sm">
                  <input
                    type="checkbox"
                    checked={editForm.enabled}
                    onChange={(e) =>
                      setEditForm({
                        ...editForm,
                        enabled: e.target.checked,
                      })
                    }
                  />
                  Enabled
                </label>
              </div>

              <div className="flex justify-end gap-2 border-t border-white/10 pt-4">
                <button
                  type="button"
                  onClick={closeEdit}
                  disabled={saving}
                  className="rounded border border-white/10 px-4 py-2 text-xs text-muted-foreground hover:bg-white/5 disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={saving}
                  className="flex items-center gap-2 rounded bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                >
                  {saving && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}
