import { useState, useEffect } from "react";
import { apiFetch, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, AlertCircle, Clock } from "lucide-react";

interface AuditLog {
  id: number | string;
  action: string;
  user_id: string;
  resource: string;
  details: string;
  created_at: string;
}

export default function AIMemoryPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await apiFetch<{ items?: AuditLog[]; total?: number }>("/audit-log?limit=50");
        setLogs(res.items || []);
      } catch (err) {
        if (err instanceof ApiError && err.status === 403) {
          setError("ADMIN role required to view audit logs.");
        } else {
          setError("Failed to load decision history. Backend endpoint may require configuration.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-muted-foreground">Loading AI decision history...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">AI Memory & Decision History</h1>
      </div>

      {error ? (
        <Card className="border-amber-500/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-amber-500 mt-0.5 shrink-0" />
              <div>
                <h3 className="font-semibold text-amber-600 dark:text-amber-400">Observability Limitation</h3>
                <p className="text-sm text-muted-foreground mt-1">{error}</p>
                <p className="text-xs text-muted-foreground mt-2">
                  Note: Per institutional standards, no mock data is displayed. A dedicated /ai/decision-history 
                  endpoint is recommended for granular agent voting records.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              Recent System & Trading Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            {logs.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">No recent audit records found.</div>
            ) : (
              <div className="space-y-3">
                {logs.map((log) => (
                  <div key={log.id} className="p-3 rounded-lg border border-border bg-muted/20 flex flex-col md:flex-row md:items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant="default" className="text-xs">{log.action}</Badge>
                        <span className="text-sm font-mono text-muted-foreground">{log.resource || "System"}</span>
                      </div>
                      {log.details && <div className="text-xs text-muted-foreground mt-1 font-mono break-all">{log.details}</div>}
                    </div>
                    <div className="text-xs text-muted-foreground font-mono shrink-0">
                      {new Date(log.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
