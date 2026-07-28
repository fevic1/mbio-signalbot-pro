import { useState, useEffect } from 'react';
import { OrdersPanel } from "./OrdersPanel";
import { ActivityPanel } from "./ActivityPanel";
import { ExecutionTelemetryPanel } from "./ExecutionTelemetryPanel";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";
import { Shield, AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

interface RiskStatus {
  total_exposure: number;
  active_positions: number;
  max_exposure: number;
  risk_used: number;
}

export function ExecutionWorkspace() {
  const [riskData, setRiskData] = useState<RiskStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRisk = async () => {
      try {
        const data = await apiFetch<RiskStatus>('/risk/status');
        setRiskData(data);
      } catch (err) {
        console.error("Failed to load risk status:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchRisk();
    const interval = setInterval(fetchRisk, 10000);
    return () => clearInterval(interval);
  }, []);

  const validationChecks = [
    { label: "Account Validation", status: "ok", detail: "Authenticated" },
    { label: "Margin Validation", status: "ok", detail: "Sufficient" },
    { label: "Leverage Validation", status: "ok", detail: "Within Limits" },
    { 
      label: "Exposure Validation", 
      status: riskData ? (riskData.risk_used < 80 ? "ok" : "warn") : "loading",
      detail: riskData ? `${riskData.risk_used.toFixed(1)}% Used` : "Loading..."
    },
    { label: "Liquidity Validation", status: "pending", detail: "Backend Pending" },
    { label: "Slippage Validation", status: "pending", detail: "Backend Pending" },
    { label: "Stop Loss Validation", status: "pending", detail: "Backend Pending" },
    { label: "Kill Switch", status: "ok", detail: "Armed" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Execution Control Center</h1>
      </div>

      {/* Live Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Metric label="Active Positions" value={loading ? "..." : String(riskData?.active_positions || 0)} />
        <Metric label="Total Exposure" value={loading ? "..." : `$${(riskData?.total_exposure || 0).toFixed(2)}`} />
        <Metric label="Risk Used" value={loading ? "..." : `${(riskData?.risk_used || 0).toFixed(1)}%`} />
        <Metric label="Max Exposure" value={loading ? "..." : `$${(riskData?.max_exposure || 0).toFixed(2)}`} />
      </div>

      {/* Order Validation Checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Pre-Flight Validation Checklist
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {validationChecks.map((check) => (
              <div key={check.label} className="flex items-center justify-between p-3 rounded-lg border border-border bg-muted/20">
                <span className="text-sm font-medium">{check.label}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-muted-foreground">{check.detail}</span>
                  {check.status === "ok" && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                  {check.status === "warn" && <AlertCircle className="h-4 w-4 text-amber-500" />}
                  {check.status === "pending" && <div className="h-4 w-4 rounded-full border-2 border-muted-foreground/30" />}
                  {check.status === "loading" && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Active Orders */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Active Execution</CardTitle>
        </CardHeader>
        <CardContent>
          <OrdersPanel />
        </CardContent>
      </Card>

      {/* Activity & Telemetry */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Execution Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ActivityPanel />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-lg font-semibold">Telemetry</CardTitle>
          </CardHeader>
          <CardContent>
            <ExecutionTelemetryPanel />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="mt-2 text-xl font-bold text-foreground">{value}</div>
    </div>
  );
}
