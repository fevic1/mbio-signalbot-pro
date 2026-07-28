import { useState, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, BarChart3 } from "lucide-react";

interface Trade {
  pnl: number;
  pnl_pct: number;
  strategy: string;
}

interface AnalyticsData {
  total_trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  total_pnl: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
}

export function RiskMetricsPanel() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch trade history to calculate real metrics
        const historyRes = await apiFetch<{ trades: Trade[] }>("/trade-history?limit=1000");
        const trades = historyRes.trades || [];
        
        const wins = trades.filter(t => t.pnl > 0).length;
        const losses = trades.filter(t => t.pnl <= 0).length;
        const totalPnl = trades.reduce((sum, t) => sum + t.pnl, 0);
        const winRate = trades.length > 0 ? (wins / trades.length) * 100 : 0;

        // Note: Advanced metrics (Sharpe, Max DD) require backend implementation.
        // We display 0 or "Pending" to strictly adhere to "No mock data".
        setData({
          total_trades: trades.length,
          wins,
          losses,
          win_rate: winRate,
          total_pnl: totalPnl,
          sharpe_ratio: 0, // Pending backend calculation
          max_drawdown_pct: 0 // Pending backend calculation
        });
      } catch (err) {
        console.error("Failed to load risk metrics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Card><CardContent className="p-6 text-sm text-muted-foreground">Calculating risk metrics...</CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-primary" />
          Performance & Risk Metrics
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <Metric label="Total Trades" value={String(data?.total_trades || 0)} />
          <Metric label="Win Rate" value={`${(data?.win_rate || 0).toFixed(1)}%`} highlight={(data?.win_rate || 0) >= 50} />
          <Metric label="Total PnL" value={`$${(data?.total_pnl || 0).toFixed(2)}`} highlight={(data?.total_pnl || 0) >= 0} />
          <Metric label="Sharpe Ratio" value={data?.sharpe_ratio === 0 ? "Pending" : String(data?.sharpe_ratio)} pending={data?.sharpe_ratio === 0} />
        </div>
        
        {data?.sharpe_ratio === 0 && (
          <div className="mt-4 flex items-start gap-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5 shrink-0" />
            <p className="text-xs text-amber-600 dark:text-amber-400">
              Advanced risk metrics (Sharpe, Max Drawdown, Correlation) are pending backend calculation. 
              Displaying live trade history aggregates only to ensure zero mock data.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Metric({ label, value, highlight, pending }: { label: string; value: string; highlight?: boolean; pending?: boolean }) {
  return (
    <div className="rounded-lg border border-border bg-muted/20 p-3">
      <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className={`mt-1 text-lg font-bold ${pending ? "text-muted-foreground italic" : (highlight ? "text-green-500" : "text-red-500")}`}>
        {value}
      </div>
    </div>
  );
}
