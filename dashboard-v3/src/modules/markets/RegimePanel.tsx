import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
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

export function RegimePanel({ defaultAsset = "" }: { defaultAsset?: string }) {
  const [selectedAsset, setSelectedAsset] = useState(defaultAsset);
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [data, setData] = useState<RegimeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [assetsLoading, setAssetsLoading] = useState(true);

  // Fetch available assets dynamically from HIP-4
  useEffect(() => {
    const fetchAssets = async () => {
      try {
        setAssetsLoading(true);
        const response = await fetch('/api/dashboard/assets');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const assets = await response.json();
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
      const response = await fetch(`/api/dashboard/regime?asset=${asset}`);
      if (!response.ok) throw new Error("Failed to fetch regime data");
      const json: RegimeData = await response.json();
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

  // Add this effect to refresh state when asset changes
  useEffect(() => {
    const refreshState = async () => {
      try {
        await fetch('/api/dashboard/refresh-state', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (err) {
        console.error("Failed to refresh state:", err);
      }
    };
    
    if (selectedAsset) {
      refreshState();
    }
  }, [selectedAsset]);

  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case "TRENDING": return "text-emerald-400";
      case "BREAKOUT": return "text-amber-400";
      case "RANGING": return "text-blue-400";
      default: return "text-gray-400";
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
    return <Card className="w-full"><CardContent className="p-6 text-sm text-muted-foreground">Loading asset universe from exchange...</CardContent></Card>;
  }

  if (availableAssets.length === 0) {
    return (
      <Card className="w-full border-red-500/50">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-red-400">
            <AlertCircle className="h-4 w-4" />
            <span>Failed to load assets from exchange. Please check connection.</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (loading && !data) {
    return <Card className="w-full"><CardContent className="p-6 text-sm text-muted-foreground">Loading regime analysis...</CardContent></Card>;
  }

  return (
    <Card className="w-full">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="text-sm font-semibold flex items-center gap-2">
          <Activity className="h-4 w-4 text-muted-foreground" />
          Market Regime
        </div>
        {/* Dynamic Asset Selector */}
        <div className="relative">
          <select 
            value={selectedAsset} 
            onChange={(e) => setSelectedAsset(e.target.value)}
            className="appearance-none bg-muted border border-border rounded px-2 py-1 text-xs font-mono pr-6 cursor-pointer focus:outline-none focus:ring-1 focus:ring-emerald-500"
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
          <div className="text-sm text-red-400">Error: {error}</div>
        ) : data && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className={`flex items-center gap-2 text-2xl font-bold ${getRegimeColor(data.regime)}`}>
                {getRegimeIcon(data.regime)}
                {data.regime}
              </div>
              <div className="text-right">
                <div className="text-xs text-muted-foreground">Confidence</div>
                <div className="text-xl font-semibold">{(data.confidence * 100).toFixed(1)}%</div>
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

            <div className="grid grid-cols-3 gap-2 pt-2 text-center">
              <div className="p-2 bg-muted/50 rounded-md">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Momentum</div>
                <div className="font-mono text-sm font-medium">{data.momentum.toFixed(2)}</div>
              </div>
              <div className="p-2 bg-muted/50 rounded-md">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Volatility</div>
                <div className="font-mono text-sm font-medium">{data.volatility.toFixed(2)}</div>
              </div>
              <div className="p-2 bg-muted/50 rounded-md">
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Mean Rev.</div>
                <div className="font-mono text-sm font-medium">{data.mean_reversion.toFixed(2)}</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
