const API_BASE = import.meta.env.VITE_API_URL || ''

async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({
      error: res.statusText,
      detail: res.statusText,
    }))

    throw new Error(
      body.error ||
      body.detail ||
      body.message ||
      `HTTP ${res.status}`,
    )
  }

  return res.json() as Promise<T>
}

export const mcpApi = {
  validateConfig(config: unknown) {
    return apiFetch<{
      valid: boolean
      error?: string
    }>('/api/mcp/validate', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  },

  detectTransport(config: unknown) {
    return apiFetch<{
      transport: string
      status: string
      auth_required: boolean
    }>('/api/mcp/detect-transport', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  },

  connect(config: unknown) {
    return apiFetch<{
      status: 'ready' | 'auth_required' | 'error'
      server_id?: string
      transaction_id?: string
      authorization_url?: string
      tools?: Array<Record<string, unknown>>
      health?: Record<string, unknown>
      error?: string
    }>('/api/mcp/connect', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  },

  oauthStatus(transactionId: string) {
    return apiFetch<{
      status: string
      server_id?: string
      tools?: Array<Record<string, unknown>>
      health?: Record<string, unknown>
      error?: string
    }>(
      `/api/mcp/oauth/${encodeURIComponent(transactionId)}/status`,
    )
  },

  listServers() {
    return apiFetch<{
      servers: Array<Record<string, unknown>>
    }>('/api/mcp/servers')
  },

  healthCheck(serverId: string) {
    return apiFetch<{
      status: string
      transport?: string
      error?: string
    }>(`/api/mcp/${encodeURIComponent(serverId)}/health`)
  },

  deleteServer(serverId: string) {
    return apiFetch<{ deleted: boolean }>(
      `/api/mcp/${encodeURIComponent(serverId)}`,
      { method: 'DELETE' },
    )
  },

  updateServer(serverId: string, payload: unknown) {
    return apiFetch<{
      status: string
      server_id: string
    }>(
      `/api/dashboard/mcp/servers/${encodeURIComponent(serverId)}`,
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      },
    )
  },
}

export default mcpApi
