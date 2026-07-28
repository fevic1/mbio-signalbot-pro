import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiFetch } from '@/lib/api';
import { Activity, TrendingUp, Minus, Zap, ChevronDown, AlertCircle } from 'lucide-react';

interface RegimeData {
  asset: string;
  regime: string;
  confidence: number;
  momentum: number;
  volatility: number;
  mean_reversion: number;
  is_cached: boolean;
}

export function RegimePanel({
  defaultAsset = "BTC",
  onAssetChange,
}: {
  defaultAsset?: string;
  onAssetChange?: (asset: string) => void;
}) {
  const [selectedAsset, setSelectedAsset] = useState(defaultAsset);
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [data, setData] = useState<RegimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assetsLoading, setAssetsLoading] = useState(true);

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        setAssetsLoading(true);
        const assets = await apiFetch<string[]>('/assets');
        if (!assets || assets.length === 0) {
          throw new Error("No assets available from exchange");
        }
        setAvailableAssets(assets);
        if (!selectedAsset && assets.length > 0) {
          setSelectedAsset(assets[0]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load assets");
        setAvailableAssets([]);
      } finally {
        setAssetsLoading(false);
      }
    };
    fetchAssets();
  }, []);

  const fetchRegime = async (asset: string) => {
    if (!asset) return;
    try {
      setLoading(true);
      const json = await apiFetch<RegimeData>(`/regime?asset=${asset}`);
      setData(json);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedAsset) {
      fetchRegime(selectedAsset);
      const interval = setInterval(() => fetchRegime(selectedAsset), 15000);
      return () => clearInterval(interval);
    }
  }, [selectedAsset]);

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case "TRENDING": return "text-emerald-400";
      case "BREAKOUT": return "text-amber-400";
      case "RANGING": return "text-blue-400";
      default: return "text-muted-foreground";
    }
  };

  const getRegimeIcon = (regime: string) => {
    switch (regime) {
      case "TRENDING": return <TrendingUp className="h-5 w-5" />;
      case "BREAKOUT": return <Zap className="h-5 w-5" />;
      case "RANGING": return <Minus className="h-5 w-5" />;
      default: return <Activity className="h-5 w-5" />;
    }
  };

  if (assetsLoading) {
    return <Card><CardContent className="p-6 text-sm text-muted-foreground">Loading asset universe...</CardContent></Card>;
  }

  if (availableAssets.length === 0) {
    return (
      <Card className="border-destructive/50">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span>Failed to load assets from exchange.</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading && !data) {
    return <Card><CardContent className="p-6 text-sm text-muted-foreground">Loading regime analysis...</CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-sm font-bold flex items-center gap-2">
          <Activity className="h-4 w-4 text-muted-foreground" />
          Market Regime
        </CardTitle>
        <div className="relative">
          <select 
            value={selectedAsset} 
            onChange={(e) => { setSelectedAsset(e.target.value); onAssetChange?.(e.target.value); }}
            className="appearance-none bg-muted border border-border rounded px-2 py-1 text-xs font-mono pr-6 cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {availableAssets.map(asset => (
              <option key={asset} value={asset}>{asset}</option>
            ))}
          </select>
          <ChevronDown className="h-3 w-3 absolute right-2 top-1.5 text-muted-foreground pointer-events-none" />
        </div>
      </CardHeader>
      <CardContent>
        {error ? (
          <div className="text-sm text-destructive">Error: {error}</div>
        ) : data && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className={`flex items-center gap-2 text-2xl font-bold ${getRegimeColor(data.regime)}`}>
                {getRegimeIcon(data.regime)}
                {data.regime}
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Confidence</div>
                <div className="text-3xl font-bold">{(data.confidence * 100).toFixed(1)}%</div>
              </div>
            </div>

            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  data.regime === "TRENDING" ? "bg-emerald-500" : 
                  data.regime === "BREAKOUT" ? "bg-amber-500" : "bg-blue-500"
                }`}
                style={{ width: `${Math.max(5, data.confidence * 100)}%` }}
              ></div>
            </div>

            <div className="grid grid-cols-3 gap-4 pt-4">
              <div className="rounded-lg border border-border bg-muted/20 p-4">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Momentum</div>
                <div className="mt-2 font-mono text-lg font-bold">{data.momentum.toFixed(2)}</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-4">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Volatility</div>
                <div className="mt-2 font-mono text-lg font-bold">{data.volatility.toFixed(2)}</div>
              </div>
              <div className="rounded-lg border border-border bg-muted/20 p-4">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Mean Rev.</div>
                <div className="mt-2 font-mono text-lg font-bold">{data.mean_reversion.toFixed(2)}</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
