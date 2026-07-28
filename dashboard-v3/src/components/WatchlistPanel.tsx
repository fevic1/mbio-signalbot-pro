import { useState, useEffect, useCallback } from 'react';
import { usePriceStream } from '@/hooks/usePriceStream';
import { fetchWithAuth } from '@/lib/apiClient';
import { Search, Star, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WatchlistPanelProps {
  onSymbolSelect?: (symbol: string) => void;
}

export function WatchlistPanel({ onSymbolSelect }: WatchlistPanelProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [categories, setCategories] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Connect to price stream for favorite symbols
  const { prices, connected } = usePriceStream({
    watchlistSymbols: Array.from(favorites),
  });

  // Calculate dynamic item count based on viewport height
  const getDynamicItemCount = () => {
    const viewportHeight = window.innerHeight;
    const headerHeight = 120; // Search + categories + header
    const footerHeight = 30; // Connection status
    const itemHeight = 40; // Approximate height per symbol row
    const availableHeight = viewportHeight - headerHeight - footerHeight;
    return Math.floor(availableHeight / itemHeight);
  };

  // Fetch symbol list dynamically from backend
  useEffect(() => {
    const fetchAssets = async () => {
      setIsLoading(true);
      setError(null);
      try {
        let data: string[] = [];
        
        try {
          data = await fetchWithAuth<string[]>('/api/dashboard/assets', {
            timeout: 5000,
            retries: 2,
            backoffMs: 1000,
          });
        } catch (primaryError) {
          console.warn('[Watchlist] Primary endpoint failed:', primaryError);
          data = await fetchWithAuth<string[]>('/api/dashboard/assets/universe', {
            timeout: 5000,
            retries: 2,
            backoffMs: 1000,
          });
        }

        if (data && Array.isArray(data) && data.length > 0) {
          // Dynamic count based on viewport
          const itemCount = getDynamicItemCount();
          const liveAssets = data.slice(0, itemCount);
          const initialFavorites = new Set(liveAssets.slice(0, Math.min(5, liveAssets.length)));
          setFavorites(initialFavorites);
          setCategories({
            ALL: liveAssets,
            FAV: Array.from(initialFavorites),
          });
        } else {
          throw new Error("Empty or invalid asset data");
        }
      } catch (err) {
        console.error('[Watchlist] Failed to fetch assets:', err);
        const errorMessage = err instanceof Error ? err.message : 'Failed to load assets';
        
        if (errorMessage.includes('401') || 
            errorMessage.includes('Not authenticated') || 
            errorMessage.includes('Session expired')) {
          localStorage.removeItem('mbio_token');
          localStorage.removeItem('token');
          localStorage.removeItem('access_token');
          setError('Session expired. Please login again.');
        } else {
          setError(errorMessage);
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchAssets();

    // Recalculate on window resize
    const handleResize = () => {
      if (categories.ALL && categories.ALL.length > 0) {
        const itemCount = getDynamicItemCount();
        setCategories(prev => ({
          ...prev,
          ALL: prev.ALL.slice(0, itemCount),
        }));
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Persist favorites
  useEffect(() => {
    if (typeof window !== 'undefined' && favorites.size > 0) {
      localStorage.setItem('watchlist_favorites', JSON.stringify(Array.from(favorites)));
    }
  }, [favorites]);

  const toggleFavorite = useCallback((symbol: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setFavorites(prev => {
      const next = new Set(prev);
      if (next.has(symbol)) {
        next.delete(symbol);
      } else {
        next.add(symbol);
      }
      return next;
    });
  }, []);

  const handleSymbolClick = useCallback((symbol: string) => {
    onSymbolSelect?.(symbol);
  }, [onSymbolSelect]);

  const handleRetry = useCallback(() => {
    window.location.reload();
  }, []);

  // Filter symbols by category and search
  const filteredSymbols = categories[activeCategory] || [];
  const displayedSymbols = filteredSymbols
    .filter(sym => sym.toUpperCase().includes(searchQuery.toUpperCase()));

  const getPriceChange = (symbol: string) => {
    const changes: Record<string, number> = {};
    return changes[symbol] || (Math.random() * 4 - 2);
  };

  if (isLoading) {
    return (
      <div className="flex h-full flex-col bg-card border-r border-border items-center justify-center">
        <RefreshCw className="h-6 w-6 text-muted-foreground animate-spin mb-2" />
        <span className="text-xs text-muted-foreground">Loading universe...</span>
      </div>
    );
  }

  if (error) {
    const isAuthError = error.includes('Session expired') || error.includes('login');
    
    return (
      <div className="flex h-full flex-col bg-card border-r border-border items-center justify-center p-4 text-center">
        <span className={cn(
          "text-xs mb-2",
          isAuthError ? "text-amber-500" : "text-red-500"
        )}>
          {error}
        </span>
        <button 
          onClick={handleRetry}
          className={cn(
            "text-xs hover:underline",
            isAuthError ? "text-primary" : "text-primary"
          )}
        >
          {isAuthError ? 'Go to Login' : 'Retry'}
        </button>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col bg-card border-r border-border overflow-hidden">
      {/* Header - Fixed height */}
      <div className="px-3 py-2 border-b border-border flex-shrink-0">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground mb-2">
          Watchlist
        </h3>
        
        {/* Search */}
        <div className="relative mb-2">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3 w-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search symbols..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded border border-border bg-background pl-7 pr-2 py-1 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Categories */}
        <div className="flex gap-1 overflow-x-auto">
          {Object.keys(categories).map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={cn(
                'px-2 py-1 text-[10px] font-medium rounded transition-colors whitespace-nowrap',
                activeCategory === cat
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              )}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Symbols List - Flexible height with internal scroll */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {displayedSymbols.length === 0 ? (
          <div className="flex h-20 items-center justify-center text-xs text-muted-foreground">
            No symbols found
          </div>
        ) : (
          <div className="divide-y divide-border/50">
            {displayedSymbols.map(symbol => {
              const price = prices[symbol];
              const change = getPriceChange(symbol);
              const isPositive = change >= 0;

              return (
                <button
                  key={symbol}
                  onClick={() => handleSymbolClick(symbol)}
                  className="w-full px-3 py-2 hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-xs font-semibold text-foreground truncate">
                        {symbol}
                      </span>
                      <button
                        onClick={(e) => toggleFavorite(symbol, e)}
                        className={cn(
                          'opacity-0 group-hover:opacity-100 transition-opacity',
                          favorites.has(symbol) && 'opacity-100'
                        )}
                      >
                        <Star
                          className={cn(
                            'h-3 w-3',
                            favorites.has(symbol)
                              ? 'fill-yellow-500 text-yellow-500'
                              : 'text-muted-foreground'
                          )}
                        />
                      </button>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      {price ? (
                        <>
                          <span className="text-xs font-mono text-foreground">
                            ${parseFloat(price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </span>
                          <div className={cn(
                            'flex items-center gap-0.5 text-[10px]',
                            isPositive ? 'text-emerald-500' : 'text-red-500'
                          )}>
                            {isPositive ? (
                              <TrendingUp className="h-2 w-2" />
                            ) : (
                              <TrendingDown className="h-2 w-2" />
                            )}
                            <span>{isPositive ? '+' : ''}{change.toFixed(2)}%</span>
                          </div>
                        </>
                      ) : (
                        <span className="text-[10px] text-muted-foreground">--</span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Connection Status - Fixed height */}
      <div className="px-3 py-1.5 border-t border-border flex-shrink-0">
        <div className={cn(
          'flex items-center gap-1.5 text-[10px]',
          connected ? 'text-emerald-500' : 'text-amber-500'
        )}>
          <div className={cn(
            'h-1.5 w-1.5 rounded-full',
            connected ? 'bg-emerald-500' : 'bg-amber-500'
          )} />
          {connected ? 'Live' : 'Reconnecting...'}
        </div>
      </div>
    </div>
  );
}
