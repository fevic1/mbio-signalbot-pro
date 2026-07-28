import { useState, useEffect } from 'react';
import { apiFetch } from '@/lib/api';

interface Asset {
  symbol: string;
  name: string;
  logo_url: string;
  category: string;
  price: number;
  volume_24h: number;
  change_24h: number;
  funding_rate: number;
  max_leverage: number;
  sz_decimals: number;
  type: string;
}

const formatUSD = (value: number): string => {
  if (value >= 1.0) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);
  }
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 3, maximumFractionDigits: 6 }).format(value);
};

const AssetsTable: React.FC = () => {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchAssets = async () => {
      try {
        setLoading(true);
        const data = await apiFetch<{ success: boolean; assets: Asset[] }>('/assets/universe');
        if (data.success) {
          setAssets(data.assets);
        }
      } catch (err) {
        console.error("Failed to load live Hyperliquid assets:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchAssets();
    const interval = setInterval(fetchAssets, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>, symbol: string) => {
    const img = e.currentTarget;
    if (!img.dataset.fallbackAttempted) {
      img.dataset.fallbackAttempted = 'coincap';
      img.src = `https://assets.coincap.io/assets/icons/${symbol.toLowerCase()}@2x.png`;
    } else if (img.dataset.fallbackAttempted === 'coincap') {
      img.dataset.fallbackAttempted = 'svg';
      img.style.display = 'none';
      const fallbackDiv = document.createElement('div');
      fallbackDiv.className = 'w-7 h-7 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold shrink-0 border border-primary/30';
      fallbackDiv.textContent = symbol.slice(0, 2).toUpperCase();
      img.parentNode?.insertBefore(fallbackDiv, img.nextSibling);
    }
  };

  const filteredAssets = assets.filter(asset => 
    asset.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading && assets.length === 0) {
    return <div className="p-8 text-center text-muted-foreground">Loading live market data...</div>;
  }

  return (
    <div className="w-full rounded-xl border border-border bg-card p-6">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search trading universe..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full max-w-md rounded-lg border border-border bg-background px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm text-left">
          <thead className="text-xs uppercase text-muted-foreground bg-muted/50 border-b border-border">
            <tr>
              <th className="p-4 w-12">#</th>
              <th className="p-4">Asset</th>
              <th className="p-4">Category</th>
              <th className="p-4">24h Volume</th>
              <th className="p-4">Price</th>
              <th className="p-4">24h Change</th>
              <th className="p-4">Max Lev</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {filteredAssets.map((asset, index) => (
              <tr key={asset.symbol} className="hover:bg-muted/30 transition-colors cursor-pointer group">
                <td className="p-4 text-muted-foreground font-mono text-xs w-12">{index + 1}</td>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <img 
                      src={asset.logo_url} 
                      onError={(e) => handleImageError(e, asset.symbol)}
                      className="w-7 h-7 rounded-full object-cover bg-background border border-border shrink-0" 
                      alt={asset.symbol}
                    />
                    <div>
                      <span className="font-bold text-foreground group-hover:text-primary">{asset.symbol}</span>
                      <span className="text-[10px] ml-1.5 px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20 font-semibold uppercase">
                        {asset.type}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="p-4 text-muted-foreground text-xs font-semibold uppercase">{asset.category}</td>
                <td className="p-4 font-mono font-medium text-sm text-foreground">{formatUSD(asset.volume_24h)}</td>
                <td className="p-4 font-mono font-bold text-sm text-foreground">{formatUSD(asset.price)}</td>
                <td className={`p-4 font-mono text-sm font-semibold ${asset.change_24h >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {asset.change_24h >= 0 ? '+' : ''}{asset.change_24h.toFixed(2)}%
                </td>
                <td className="p-4 font-mono text-xs text-green-500 font-semibold">{asset.max_leverage}x</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssetsTable;
