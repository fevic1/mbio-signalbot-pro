import { useMemo, useState } from 'react'
import useMCPFlow from './useMCPFlow'

interface Props {
  onClose: () => void
  onSuccess?: (result: {
    serverId: string
    tools: Array<Record<string, unknown>>
  }) => void
}

export default function MCPAddWizard({ onClose, onSuccess }: Props) {
  const flow = useMCPFlow()

  const [form, setForm] = useState({
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
  })

  const runningLabel = useMemo(() => {
    const labels: Record<string, string> = {
      validate: 'Validating',
      transport: 'Detecting transport',
      connect: 'Connecting',
      authenticate: 'Authenticating',
      discover: 'Discovering tools',
      register: 'Registering tools',
      health: 'Checking health',
    }
    return labels[flow.step] || 'Working'
  }, [flow.step])

  const submit = async (event: React.FormEvent) => {
    event.preventDefault()

    try {
      const generatedServerId =
        form.name
          .trim()
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '-')
          .replace(/^-+|-+$/g, '') || 'mcp-server'

      const auth =
        form.auth_type === 'api_key' && form.api_key.trim()
          ? {
              type: 'api_key',
              key: form.api_key.trim(),
              header: form.auth_header || 'X-API-Key',
            }
          : form.auth_type === 'bearer' && form.auth_token.trim()
            ? {
                type: 'bearer',
                token: form.auth_token.trim(),
              }
            : { type: 'none' }

      const result = await flow.runFlow({
        ...form,
        server_id: generatedServerId,
        auth,
      })

      if (result) {
        if (!result.serverId) {
          throw new Error("MCP flow completed without a server ID")
        }

        onSuccess?.({
          serverId: result.serverId,
          tools: result.tools,
        })
      }
    } catch {
      // Error is rendered by the flow state.
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-background shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <div>
            <h2 className="text-sm font-bold">Add MCP Server</h2>
            <p className="mt-1 text-xs text-muted-foreground">
              Standard MCP transport and authentication
            </p>
          </div>

          <button
            onClick={flow.isRunning ? flow.cancel : onClose}
            className="text-xs text-muted-foreground hover:text-white"
          >
            {flow.isRunning ? 'Cancel' : 'Close'}
          </button>
        </div>

        <form onSubmit={submit} className="space-y-4 p-5">
          <div className="grid grid-cols-2 gap-3">
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                Name *
              </span>
              <input
                required
                placeholder="MCP server name"
                value={form.name}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, name: e.target.value })
                }
                className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                MCP endpoint *
              </span>
              <input
                required
                type="url"
                placeholder="https://host.example/mcp"
                value={form.endpoint}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, endpoint: e.target.value })
                }
                className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
              />
            </label>

            <label className="col-span-2 flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                Description
              </span>
              <input
                placeholder="Optional description"
                value={form.description}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, description: e.target.value })
                }
                className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                Transport
              </span>
              <select
                value={form.transport}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, transport: e.target.value })
                }
                className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="auto">Auto-detect</option>
                <option value="streamable_http">Streamable HTTP</option>
                <option value="sse">SSE</option>
              </select>
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                Authentication
              </span>
              <select
                value={form.auth_type}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, auth_type: e.target.value })
                }
                className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground"
              >
                <option value="none">Auto / discover</option>
                <option value="api_key">API key</option>
                <option value="bearer">Bearer token</option>
                <option value="oauth">OAuth</option>
              </select>
            </label>
          </div>

          {form.auth_type === 'api_key' && (
            <div className="grid grid-cols-2 gap-3">
              <label className="flex flex-col gap-1">
                <span className="text-[11px] font-medium text-muted-foreground">
                  API key
                </span>
                <input
                  type="password"
                  placeholder="Optional until required"
                  value={form.api_key}
                  disabled={flow.isRunning}
                  onChange={(e) =>
                    setForm({ ...form, api_key: e.target.value })
                  }
                  className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
                  autoComplete="off"
                />
              </label>

              <label className="flex flex-col gap-1">
                <span className="text-[11px] font-medium text-muted-foreground">
                  Header name
                </span>
                <input
                  placeholder="X-API-Key"
                  value={form.auth_header}
                  disabled={flow.isRunning}
                  onChange={(e) =>
                    setForm({ ...form, auth_header: e.target.value })
                  }
                  className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
                />
              </label>
            </div>
          )}

          {form.auth_type === 'bearer' && (
            <label className="flex flex-col gap-1">
              <span className="text-[11px] font-medium text-muted-foreground">
                Bearer token
              </span>
              <input
                type="password"
                placeholder="Optional until required"
                value={form.auth_token}
                disabled={flow.isRunning}
                onChange={(e) =>
                  setForm({ ...form, auth_token: e.target.value })
                }
                className="w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground/60"
                autoComplete="off"
              />
            </label>
          )}

          {flow.logs.length > 0 && (
            <div className="max-h-36 overflow-auto rounded border border-white/10 bg-black/30 p-3 font-mono text-[10px] text-muted-foreground">
              {flow.logs.map((entry, index) => (
                <div key={`${entry.time}-${index}`}>
                  {entry.message}
                </div>
              ))}
            </div>
          )}

          {flow.error && (
            <div className="rounded border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
              {flow.error}
            </div>
          )}

          {flow.isReady && (
            <div className="rounded border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-400">
              Ready. Discovered {flow.discoveredTools.length} tool(s).
            </div>
          )}

          <div className="flex justify-end gap-2">
            {!flow.isRunning && !flow.isReady && (
              <button
                type="submit"
                className="rounded bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-700"
              >
                Connect &amp; Discover
              </button>
            )}

            {flow.isRunning && (
              <span className="px-3 py-2 text-xs text-muted-foreground">
                {runningLabel}...
              </span>
            )}

            {flow.isReady && (
              <button
                type="button"
                onClick={onClose}
                className="rounded bg-emerald-600 px-4 py-2 text-xs font-semibold text-white"
              >
                Done
              </button>
            )}

            {flow.hasError && (
              <button
                type="button"
                onClick={flow.reset}
                className="rounded bg-muted px-4 py-2 text-xs"
              >
                Retry
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}
