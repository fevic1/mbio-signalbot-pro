import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
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
} from 'lucide-react';
import { apiFetch } from '@/lib/api';

interface McpServer {
  server_id: string;
  name: string;
  description: string;
  endpoint?: string | null;
  rate_limit_per_min: number;
  is_active: boolean;
}

interface McpFormData {
  server_id: string;
  name: string;
  description: string;
  endpoint: string;
  api_key: string;
  rate_limit_per_min: number;
  enabled: boolean;
}

const emptyForm: McpFormData = {
  server_id: '',
  name: '',
  description: '',
  endpoint: '',
  api_key: '',
  rate_limit_per_min: 60,
  enabled: true,
};

export function McpRegistryPanel() {
  const [servers, setServers] = useState<McpServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingServerId, setEditingServerId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState<McpFormData>(emptyForm);

  const fetchServers = async () => {
    try {
      const data = await apiFetch<{ servers: McpServer[] }>('/mcp/servers');
      setServers(data.servers ?? []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchServers();
  }, []);

  const resetForm = () => {
    setFormData({ ...emptyForm });
    setShowForm(false);
    setEditingServerId(null);
  };

  const handleAdd = () => {
    setFormData({ ...emptyForm });
    setEditingServerId(null);
    setShowForm(true);
  };

  const handleEdit = (server: McpServer) => {
    setFormData({
      server_id: server.server_id,
      name: server.name,
      description: server.description,
      endpoint: server.endpoint ?? '',
      api_key: '',
      rate_limit_per_min: server.rate_limit_per_min,
      enabled: server.is_active,
    });
    setEditingServerId(server.server_id);
    setShowForm(true);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (editingServerId) {
        await apiFetch(`/mcp/servers/${encodeURIComponent(editingServerId)}`, {
          method: 'PUT',
          body: JSON.stringify(formData),
        });
      } else {
        await apiFetch('/mcp/register', {
          method: 'POST',
          body: JSON.stringify(formData),
        });
      }

      resetForm();
      await fetchServers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save MCP server');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnregister = async (serverId: string) => {
    if (!confirm(`Are you sure you want to remove server '${serverId}'?`)) return;

    try {
      await apiFetch(`/mcp/unregister/${encodeURIComponent(serverId)}`, {
        method: 'POST',
      });
      await fetchServers();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove server');
    }
  };

  if (loading) {
    return (
      <Card className="rounded-2xl border-white/10 bg-white/5">
        <CardContent className="p-6 text-sm text-muted-foreground">
          Loading...
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="rounded-2xl border-white/10 bg-white/5">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="text-sm font-bold flex items-center gap-2">
          <Server className="h-4 w-4 text-muted-foreground" />
          MCP Infrastructure Registry
        </div>

        <button
          onClick={handleAdd}
          className="flex items-center gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md transition"
        >
          <Plus className="h-3 w-3" />
          Add Server
        </button>
      </CardHeader>

      <CardContent>
        {error && (
          <div className="text-red-400 text-xs mb-4">
            Error: {error}
          </div>
        )}

        {showForm && (
          <form
            onSubmit={handleSubmit}
            className="mb-6 p-4 bg-muted/30 rounded-md border border-border space-y-3"
          >
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {editingServerId
                  ? `Edit MCP Server: ${editingServerId}`
                  : 'New MCP Server Configuration'}
              </h4>

              <button
                type="button"
                onClick={resetForm}
                className="text-muted-foreground hover:text-white"
                title="Close"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <input
                required
                disabled={Boolean(editingServerId)}
                placeholder="Server ID"
                value={formData.server_id}
                onChange={(e) =>
                  setFormData({ ...formData, server_id: e.target.value })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm disabled:opacity-50"
              />

              <input
                required
                placeholder="Display Name"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm"
              />

              <input
                required
                placeholder="Description"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm col-span-2"
              />

              <input
                placeholder="MCP Endpoint"
                value={formData.endpoint}
                onChange={(e) =>
                  setFormData({ ...formData, endpoint: e.target.value })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm col-span-2"
              />

              <input
                type="password"
                placeholder={
                  editingServerId
                    ? 'API Key (leave blank to keep existing key)'
                    : 'API Key'
                }
                value={formData.api_key}
                onChange={(e) =>
                  setFormData({ ...formData, api_key: e.target.value })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm"
              />

              <input
                required
                min={1}
                type="number"
                placeholder="Rate Limit/min"
                value={formData.rate_limit_per_min}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    rate_limit_per_min: parseInt(e.target.value, 10) || 1,
                  })
                }
                className="bg-background border border-border rounded px-2 py-1 text-sm"
              />
            </div>

            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              <input
                type="checkbox"
                checked={formData.enabled}
                onChange={(e) =>
                  setFormData({ ...formData, enabled: e.target.checked })
                }
              />
              Enabled
            </label>

            <div className="flex gap-2 pt-2">
              <button
                type="submit"
                disabled={submitting}
                className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-4 py-1.5 rounded flex items-center gap-2 disabled:opacity-50"
              >
                {submitting && (
                  <Loader2 className="h-3 w-3 animate-spin" />
                )}
                {editingServerId ? 'Save Changes' : 'Register'}
              </button>

              <button
                type="button"
                onClick={resetForm}
                className="bg-muted hover:bg-muted/80 text-foreground text-xs px-4 py-1.5 rounded"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        <div className="space-y-4">
          {servers.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">
              No MCP servers registered.
            </div>
          ) : (
            servers.map((server) => (
              <div
                key={server.server_id}
                className="flex items-start justify-between rounded-xl border border-white/10 bg-black/20 p-4 group"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm font-bold text-white">
                      {server.server_id}
                    </span>

                    {server.is_active ? (
                      <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                    )}
                  </div>

                  <div className="mt-2 text-xs text-white/40">
                    {server.description}
                  </div>

                  <div className="flex items-center gap-4 text-[10px] uppercase tracking-wider text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Shield className="h-3 w-3" />
                      Rate {server.rate_limit_per_min}/min
                    </span>

                    {server.endpoint && (
                      <span className="truncate max-w-[420px]">
                        {server.endpoint}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-1 ml-4">
                  <button
                    onClick={() => handleEdit(server)}
                    className="text-muted-foreground hover:text-white hover:bg-white/10 p-2 rounded transition"
                    title="Edit Server"
                  >
                    <Pencil className="h-4 w-4" />
                  </button>

                  <button
                    onClick={() => handleUnregister(server.server_id)}
                    className="text-red-400 hover:text-red-600 hover:bg-red-500/10 p-2 rounded transition"
                    title="Remove Server"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
