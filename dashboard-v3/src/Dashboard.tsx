import { useEffect, useState } from "react";
import { LayoutDashboard, TrendingUp, Activity, Wallet, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiFetch, ApiError } from "@/lib/api";

interface OverviewData {
  hl_balance: number;
  total_balance: number;
  equity: number;
  deployed_pct: number;
  notional: number;
  open_positions: number;
  daily_pnl_pct: number;
  realized_pnl_usd: number;
  unrealized_pnl_usd: number;
  win_rate: string | number;
  total_trades: number;
  active_grids: number;
}

export default function Dashboard() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await apiFetch<OverviewData>("/overview");
        if (isMounted) {
          setData(res);
          setError(null);
        }
      } catch (e) {
        if (isMounted) {
          setError(e instanceof ApiError ? e.message : "Failed to load overview data");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();
    // Bounded polling every 10 seconds for live dashboard updates
    const interval = setInterval(fetchData, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const formatUsd = (val: number) => `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPct = (val: number) => `${val >= 0 ? "+" : ""}${val.toFixed(2)}%`;

  if (loading && !data) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        Loading dashboard data...
      </div>
    );
  }

  if (error && !data) {
    return (
      <div className="flex h-full flex-col items-center justify-center text-destructive">
        <AlertCircle className="mb-2 h-8 w-8" />
        <p>{error}</p>
      </div>
    );
  }

  const d = data || {
    hl_balance: 0, total_balance: 0, equity: 0, deployed_pct: 0, notional: 0,
    open_positions: 0, daily_pnl_pct: 0, realized_pnl_usd: 0, unrealized_pnl_usd: 0,
    win_rate: "N/A", total_trades: 0, active_grids: 0
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <LayoutDashboard className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Operational Dashboard</h1>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {/* Equity / Balance */}
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Wallet className="h-4 w-4" />
              Total Equity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatUsd(d.equity)}</div>
            <div className="text-xs text-muted-foreground mt-1">HL Balance: {formatUsd(d.hl_balance)}</div>
          </CardContent>
        </Card>

        {/* PnL */}
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              Daily PnL
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${d.daily_pnl_pct >= 0 ? "text-green-500" : "text-red-500"}`}>
              {formatPct(d.daily_pnl_pct)}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              Realized: {formatUsd(d.realized_pnl_usd)} | Unrealized: {formatUsd(d.unrealized_pnl_usd)}
            </div>
          </CardContent>
        </Card>

        {/* Active Bots / Positions */}
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
              <Activity className="h-4 w-4" />
              Active Positions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{d.open_positions}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Grids: {d.active_grids} | Trades: {d.total_trades}
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="bg-card border-border">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">ONLINE</div>
            <div className="text-xs text-muted-foreground mt-1">
              Win Rate: {d.win_rate === "N/A" ? "N/A" : `${d.win_rate}%`}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
