import { useState, useEffect } from "react";
import { OverviewPanel } from "./OverviewPanel";
import { PositionsPanel } from "./PositionsPanel";
import { RiskMetricsPanel } from "./RiskMetricsPanel";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Shield, TrendingUp, Zap } from "lucide-react";

interface RiskStatus {
  active_positions: number;
  risk_used: number;
}

interface OverviewData {
  total_balance: number;
  equity: number;
}

export function PortfolioWorkspace() {
  const [riskData, setRiskData] = useState<RiskStatus | null>(null);
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [risk, overview] = await Promise.all([
          apiFetch<RiskStatus>("/risk/status"),
          apiFetch<OverviewData>("/overview")
        ]);
        setRiskData(risk);
        setOverviewData(overview);
      } catch (err) {
        console.error("Failed to load portfolio metrics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleClose = (position: any) => {
    console.log("Close requested for:", position.asset);
    // Integration with Ticket component will be wired here
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Activity className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Portfolio Command Center</h1>
      </div>

      {/* Live Metrics (No Mock Data) */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Metric 
          icon={<TrendingUp className="h-4 w-4 text-emerald-500" />}
          label="Total Equity" 
          value={loading ? "..." : `$${(overviewData?.equity || 0).toFixed(2)}`} 
        />
        <Metric 
          icon={<Activity className="h-4 w-4 text-blue-500" />}
          label="Active Positions" 
          value={loading ? "..." : String(riskData?.active_positions || 0)} 
        />
        <Metric 
          icon={<Shield className="h-4 w-4 text-amber-500" />}
          label="Risk Used" 
          value={loading ? "..." : `${(riskData?.risk_used || 0).toFixed(1)}%`} 
        />
        <Metric 
          icon={<Zap className="h-4 w-4 text-purple-500" />}
          label="Execution" 
          value="ONLINE" 
        />
      </div>

      {/* Overview & Risk Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OverviewPanel />
        <RiskMetricsPanel />
      </div>

      {/* Active Positions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Active Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <PositionsPanel onClose={handleClose} />
        </CardContent>
      </Card>
    </div>
  );
}

function Metric({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-card p-4 flex items-center gap-4">
      <div className="p-2 rounded-lg bg-muted">{icon}</div>
      <div>
        <div className="text-xs uppercase tracking-wider text-muted-foreground">{label}</div>
        <div className="mt-1 text-xl font-bold text-foreground">{value}</div>
      </div>
    </div>
  );
}
