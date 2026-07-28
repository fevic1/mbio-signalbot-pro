import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, CheckCircle2, XCircle, Server, Clock } from "lucide-react";

interface HealthCheck {
  telegram_bot: boolean;
  config_loaded: boolean;
  exchange_connected: boolean;
  grid_state_loaded: boolean;
}

interface HealthData {
  status: "ok" | "degraded";
  checks: HealthCheck;
  uptime_sec: number;
}

interface Task {
  id: string;
  name: string;
  status: "healthy" | "stale" | "unknown" | "not_started" | "degraded";
  last_run: string;
  error_count: number;
}

interface SystemStatusData {
  tasks: Task[];
  auto_trading: boolean;
}

export default function SystemPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [systemStatus, setSystemStatus] = useState<SystemStatusData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [h, s] = await Promise.all([
          apiFetch<HealthData>("/health"),
          apiFetch<SystemStatusData>("/system/status")
        ]);
        setHealth(h);
        setSystemStatus(s);
      } catch (err) {
        console.error("Failed to load system status:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (sec: number) => {
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return `${h}h ${m}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-500 bg-green-500/10 border-green-500/20";
      case "stale": return "text-amber-500 bg-amber-500/10 border-amber-500/20";
      case "degraded": return "text-red-500 bg-red-500/10 border-red-500/20";
      default: return "text-muted-foreground bg-muted border-border";
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-muted-foreground">Loading system telemetry...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Server className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">System Health & Telemetry</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            Core Services Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {health && Object.entries(health.checks).map(([key, value]) => (
              <div key={key} className="flex items-center gap-3 p-3 rounded-lg border border-border bg-muted/20">
                {value ? <CheckCircle2 className="h-5 w-5 text-green-500" /> : <XCircle className="h-5 w-5 text-red-500" />}
                <div>
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">{key.replace("_", " ")}</div>
                  <div className="font-semibold">{value ? "Connected" : "Disconnected"}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
            <span>Overall: <Badge variant={health?.status === "ok" ? "default" : "warn"}>{health?.status.toUpperCase()}</Badge></span>
            <span>Uptime: {formatUptime(health?.uptime_sec || 0)}</span>
            <span>Auto Trading: <Badge variant={systemStatus?.auto_trading ? "default" : "default"}>{systemStatus?.auto_trading ? "ENABLED" : "DISABLED"}</Badge></span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-primary" />
            Background Task Matrix
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground">
                  <th className="p-3 font-normal">Task</th>
                  <th className="p-3 font-normal">Status</th>
                  <th className="p-3 font-normal">Last Run</th>
                  <th className="p-3 font-normal">Errors</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {systemStatus?.tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-muted/30 transition-colors">
                    <td className="p-3 font-mono">{task.name}</td>
                    <td className="p-3">
                      <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold border ${getStatusColor(task.status)}`}>
                        {task.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="p-3 text-muted-foreground">{task.last_run || "Never"}</td>
                    <td className={`p-3 font-mono ${task.error_count > 0 ? "text-red-500" : "text-muted-foreground"}`}>
                      {task.error_count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
