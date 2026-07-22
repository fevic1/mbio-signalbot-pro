import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Server, Shield, CheckCircle, XCircle, Plus, Trash2, Loader2 } from 'lucide-react';

interface McpServer {
  server_id: string;
  name: string;
  description: string;
  rate_limit_per_min: number;
  is_active: boolean;
}

export function McpRegistryPanel() {
  const [servers, setServers] = useState<McpServer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // Form State
  const [formData, setFormData] = useState({
    server_id: '', name: '', description: '', api_key: '', rate_limit_per_min: 60
  });

  const fetchServers = async () => {
    try {
      const token = localStorage.getItem('mbio_token') || localStorage.getItem('token');
      const response = await fetch('/api/dashboard/mcp/servers', {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (!response.ok) throw new Error("Failed to fetch");
      const data = await response.json();
      setServers(data.servers || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchServers(); }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const token = localStorage.getItem('mbio_token') || localStorage.getItem('token');
      const response = await fetch('/api/dashboard/mcp/register', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(formData)
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Registration failed");
      }
      setShowForm(false);
      setFormData({ server_id: '', name: '', description: '', api_key: '', rate_limit_per_min: 60 });
      await fetchServers(); // Refresh list
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to register server");
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnregister = async (serverId: string) => {
    if (!confirm(`Are you sure you want to remove server '${serverId}'?`)) return;
    try {
      const token = localStorage.getItem('mbio_token') || localStorage.getItem('token');
      const response = await fetch(`/api/dashboard/mcp/unregister/${serverId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error("Failed to remove");
      await fetchServers();
    } catch (err) {
      alert("Failed to remove server");
    }
  };

  if (loading) return <Card className="w-full"><CardContent className="p-6 text-sm text-muted-foreground">Loading...</CardContent></Card>;

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="text-sm font-semibold flex items-center gap-2">
          <Server className="h-4 w-4 text-muted-foreground" />
          MCP Server Registry
        </div>
        <button 
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-md transition"
        >
          <Plus className="h-3 w-3" /> Add Server
        </button>
      </CardHeader>
      <CardContent>
        {error && <div className="text-red-400 text-xs mb-4">Error: {error}</div>}
        
        {/* Add Server Form */}
        {showForm && (
          <form onSubmit={handleRegister} className="mb-6 p-4 bg-muted/30 rounded-md border border-border space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">New MCP Server Configuration</h4>
            <div className="grid grid-cols-2 gap-3">
              <input required placeholder="Server ID (e.g., my-agent)" value={formData.server_id} onChange={e => setFormData({...formData, server_id: e.target.value})} className="bg-background border border-border rounded px-2 py-1 text-sm" />
              <input required placeholder="Display Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="bg-background border border-border rounded px-2 py-1 text-sm" />
              <input required placeholder="Description" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} className="bg-background border border-border rounded px-2 py-1 text-sm col-span-2" />
              <input required type="password" placeholder="API Key (min 16 chars)" value={formData.api_key} onChange={e => setFormData({...formData, api_key: e.target.value})} className="bg-background border border-border rounded px-2 py-1 text-sm" />
              <input required type="number" placeholder="Rate Limit/min" value={formData.rate_limit_per_min} onChange={e => setFormData({...formData, rate_limit_per_min: parseInt(e.target.value)})} className="bg-background border border-border rounded px-2 py-1 text-sm" />
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit" disabled={submitting} className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-4 py-1.5 rounded flex items-center gap-2 disabled:opacity-50">
                {submitting ? <Loader2 className="h-3 w-3 animate-spin" /> : null} Register
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="bg-muted hover:bg-muted/80 text-foreground text-xs px-4 py-1.5 rounded">Cancel</button>
            </div>
          </form>
        )}

        {/* Server List */}
        <div className="space-y-3">
          {servers.length === 0 ? (
            <div className="text-sm text-muted-foreground text-center py-4">No MCP servers registered.</div>
          ) : (
            servers.map((server) => (
              <div key={server.server_id} className="flex items-start justify-between p-3 bg-muted/30 rounded-md border border-border/50 group">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-sm font-semibold text-foreground">{server.server_id}</span>
                    {server.is_active ? <CheckCircle className="h-3.5 w-3.5 text-emerald-500" /> : <XCircle className="h-3.5 w-3.5 text-red-500" />}
                  </div>
                  <div className="text-xs text-muted-foreground mb-2">{server.description}</div>
                  <div className="flex items-center gap-4 text-[10px] uppercase tracking-wider text-muted-foreground">
                    <span className="flex items-center gap-1"><Shield className="h-3 w-3" /> Rate: {server.rate_limit_per_min}/min</span>
                  </div>
                </div>
                <button 
                  onClick={() => handleUnregister(server.server_id)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-red-400 hover:text-red-600 p-2"
                  title="Remove Server"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
