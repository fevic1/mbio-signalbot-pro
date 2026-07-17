import React, { useState, useEffect } from 'react';

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
        // Fetches the fixed backend endpoint
        const response = await fetch('/api/dashboard/assets/universe');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
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
    // Auto-refresh asset table contexts every 15 seconds
    const interval = setInterval(fetchAssets, 15000);
    return () => clearInterval(interval);
  }, []);

  /**
   * 3-Tier Resilient Avatar Fallback (Institutional Standard)
   * Tier 1: Hyperliquid Native CDN
   * Tier 2: Coincap Asset CDN
   * Tier 3: Deterministic SVG Letter Avatar
   */
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>, symbol: string) => {
    const img = e.currentTarget;
    if (!img.dataset.fallbackAttempted) {
      // Fallback Tier 1: Coincap asset CDN
      img.dataset.fallbackAttempted = 'coincap';
      img.src = `https://assets.coincap.io/assets/icons/${symbol.toLowerCase()}@2x.png`;
    } else if (img.dataset.fallbackAttempted === 'coincap') {
      // Fallback Tier 2: SVG Letter Avatar
      img.dataset.fallbackAttempted = 'svg';
      img.style.display = 'none';
      
      const fallbackDiv = document.createElement('div');
      fallbackDiv.className = 'w-7 h-7 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-xs font-bold shrink-0 border border-blue-500/30';
      fallbackDiv.textContent = symbol.slice(0, 2).toUpperCase();
      img.parentNode?.insertBefore(fallbackDiv, img.nextSibling);
    }
  };

  const filteredAssets = assets.filter(asset => 
    asset.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading && assets.length === 0) {
    return <div className="p-8 text-center text-gray-400">Loading live market data...</div>;
  }

  return (
    <div className="w-full">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search assets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full max-w-md px-4 py-2 bg-gray-900 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        />
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-800">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-400 uppercase bg-gray-900/80 border-b border-gray-800">
            <tr>
              <th className="p-4 w-12">#</th>
              <th className="p-4">Asset</th>
              <th className="p-4">Category</th>
              <th className="p-4">24h Volume</th>
              <th className="p-4">Price</th>
              <th className="p-4">Regime</th>
              <th className="p-4">Max Lev</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/50 bg-gray-900/30">
            {filteredAssets.map((asset, index) => (
              <tr 
                key={asset.symbol} 
                className="hover:bg-gray-800/40 transition cursor-pointer group"
                onClick={() => {
                  // Dynamically populates the Quick Ticket sidebar
                  const input = document.getElementById('quick-ticket-asset-input') as HTMLInputElement;
                  if (input) {
                    input.value = asset.symbol;
                    input.classList.add('ring-2', 'ring-blue-500');
                    setTimeout(() => input.classList.remove('ring-2', 'ring-blue-500'), 600);
                  }
                }}
              >
                <td className="p-4 text-gray-500 font-mono text-xs w-12">{index + 1}</td>
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <img 
                      src={asset.logo_url} 
                      onError={(e) => handleImageError(e, asset.symbol)}
                      className="w-7 h-7 rounded-full object-cover bg-gray-900 border border-gray-800 shrink-0" 
                      alt={asset.symbol}
                    />
                    <div>
                      <span className="font-bold text-white group-hover:text-blue-400 transition">{asset.symbol}</span>
                      <span className="text-[10px] ml-1.5 px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/10 font-semibold uppercase">
                        {asset.type}
                      </span>
                    </div>
                  </div>
                </td>
                <td className="p-4 text-gray-400 text-xs font-semibold uppercase">{asset.category}</td>
                <td className="p-4 font-mono font-medium text-sm text-gray-200">{formatUSD(asset.volume_24h)}</td>
                <td className="p-4 font-mono font-bold text-sm text-white">{formatUSD(asset.price)}</td>
                <td className="p-4">
                  <span className="inline-flex items-center rounded bg-gray-800 px-2 py-1 text-xs font-semibold text-gray-400">
                    RANGING
                  </span>
                </td>
                <td className="p-4 font-mono text-xs text-green-400 font-semibold">{asset.max_leverage}x</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssetsTable;
