import { useEffect, useState, useCallback, useRef, useMemo } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { RefreshCw, Search, Wifi, WifiOff, TrendingUp, Minimize2, Zap, ChevronDown, ChevronUp } from "lucide-react"
import { Sparkline } from "./Sparkline"

interface AssetData {
  name: string
  symbol?: string
  logo_url?: string
  rank?: number
  category: string
  volume_24h: number
  price: number | null
  change_24h?: number
  sparkline?: number[]
  regime?: "TRENDING" | "RANGING" | "BREAKOUT"
  correlation_group?: string
  sz_decimals?: number
  max_leverage: number
  is_isolated_only?: boolean
  exchange?: "Hyperliquid" | "Bybit"
}

interface UniverseResponse {
  exchange?: string
  total: number
  last_refresh_age?: number
  categories?: string[]
  assets: AssetData[]
}

const POLL_INTERVAL_MS = 300_000

function regimeBadge(regime?: string) {
  if (!regime) return null
  const config = {
    TRENDING: { color: "bg-long/20 text-long border-long/30", icon: TrendingUp, label: "TRENDING" },
    BREAKOUT: { color: "bg-warn/20 text-warn border-warn/30", icon: Zap, label: "BREAKOUT" },
    RANGING: { color: "bg-secondary text-muted-foreground border-border", icon: Minimize2, label: "RANGING" }
  }
  const style = config[regime as keyof typeof config] || config.RANGING
  const Icon = style.icon


  return (
    <Badge className={cn("flex items-center gap-1 font-mono text-[10px] border", style.color)}>
      <Icon className="h-3 w-3" />
      {style.label}
    </Badge>
  )
}

function correlationBadge(group?: string) {
  if (!group) return null
  const colors: Record<string, string> = {
    "BTC-ETH-SOL": "bg-blue-500/20 text-blue-400",
    "uncorrelated": "bg-secondary text-muted-foreground",
    "meme": "bg-purple-500/20 text-purple-400"
  }
  return <span className={cn("px-1.5 py-0.5 rounded text-[10px] font-mono", colors[group] || colors["uncorrelated"])}>{group}</span>
}

interface AssetUniversePanelProps {
  onTradeAsset?: (asset: string, side?: "BUY" | "SELL") => void
}

export function AssetUniversePanel({ onTradeAsset }: AssetUniversePanelProps) {
  const [data, setData] = useState<UniverseResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [exchange, setExchange] = useState<"hyperliquid" | "bybit">("hyperliquid")
  const [category, setCategory] = useState<string>("")
  const [search, setSearch] = useState<string>("")
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [livePrices, setLivePrices] = useState<Record<string, string>>({})
  const [sseConnected, setSseConnected] = useState(false)
  
  // FIX: Simple boolean state for collapse
  const [isCollapsed, setIsCollapsed] = useState(false)
  // Sorting state for client-side reordering
  const [sortKey, setSortKey] = useState<'volume_24h' | 'change_24h'>('volume_24h')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Client-side sorting: re-order assets without backend call
  const sortedAssets = useMemo(() => {
    if (!data?.assets) return []
    const assets = [...data.assets]
    assets.sort((a, b) => {
      const aVal = a[sortKey] ?? 0
      const bVal = b[sortKey] ?? 0
      return sortOrder === 'asc' ? (aVal - bVal) : (bVal - aVal)
    })
    return assets.map((a, i) => ({ ...a, rank: i + 1 }))
  }, [data?.assets, sortKey, sortOrder])


  
  const sseRef = useRef<EventSource | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams({ exchange, category, search })
      const res = await apiFetch<UniverseResponse>(`/assets/universe?${params}`)
      setData(res)
      setError(null)
      setLastUpdated(new Date())
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Failed to load asset universe")
    } finally {
      setLoading(false)
    }
  }, [exchange, category, search])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [fetchData])

  useEffect(() => {
    if (exchange !== "hyperliquid") return
    const connectSSE = () => {
      const sse = new EventSource('/api/dashboard/stream/prices')
      sse.onopen = () => setSseConnected(true)
      sse.onmessage = (event) => {
        try { setLivePrices(JSON.parse(event.data)) } catch {}
      }
      sse.onerror = () => {
        setSseConnected(false)
        sse.close()
        setTimeout(connectSSE, 5000)
      }
      sseRef.current = sse
    }
    connectSSE()
    return () => { if (sseRef.current) sseRef.current.close() }
  }, [exchange])

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>, symbol: string) => {
    const img = e.currentTarget
    if (!img.dataset.fallbackAttempted) {
      img.dataset.fallbackAttempted = 'coincap'
      img.src = `https://assets.coincap.io/assets/icons/${symbol.toLowerCase()}@2x.png`
    } else if (img.dataset.fallbackAttempted === 'coincap') {
      img.dataset.fallbackAttempted = 'svg'
      img.style.display = 'none'
      const fallbackDiv = document.createElement('div')
      fallbackDiv.className = 'w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-[10px] font-bold shrink-0 border border-blue-500/30'
      fallbackDiv.textContent = symbol.slice(0, 2).toUpperCase()
      img.parentNode?.insertBefore(fallbackDiv, img.nextSibling)
    }
  }

  if (error && !data) {
    return <div className="p-3 text-xs text-short">{error}</div>
  }

  return (
    <div className="flex flex-col h-full space-y-2">
      {/* Header Controls - Always Visible */}
      <Card className="shrink-0">
        <CardContent className="p-3">
          <div className="flex flex-wrap items-center gap-2">
            <select value={exchange} onChange={(e) => setExchange(e.target.value as any)} className="h-7 rounded-md border border-input bg-background px-2 py-1 text-xs">
              <option value="hyperliquid">Hyperliquid</option>
              <option value="bybit">Bybit</option>
            </select>
            
            <select value={category} onChange={(e) => setCategory(e.target.value)} className="h-7 rounded-md border border-input bg-background px-2 py-1 text-xs">
              <option value="">All categories</option>
              {data?.categories?.map((cat) => <option key={cat} value={cat}>{cat}</option>)}
            </select>
            
            <div className="relative flex-1 min-w-[150px]">
              <Search className="absolute left-2 top-2 h-3 w-3 text-muted-foreground" />
              <input placeholder="Search assets..." className="w-full rounded-md border border-input bg-background pl-6 pr-3 py-1 text-xs" value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            
            <Button variant="ghost" size="sm" className="h-7 w-7" onClick={fetchData} disabled={loading}>
              <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
            </Button>

            <div className={cn("flex items-center gap-1.5 px-2 py-1 rounded-md text-xs", sseConnected ? "bg-long/10 text-long" : "bg-secondary text-muted-foreground")}>
              {sseConnected ? <Wifi className="h-3 w-3" /> : <WifiOff className="h-3 w-3" />}
              <span>{sseConnected ? "Live" : "Offline"}</span>
            </div>

            {/* FIX: Actual working collapse button */}
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="ml-auto shrink-0 flex items-center gap-1"
            >
              {isCollapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
              <span className="text-xs">{isCollapsed ? "Expand" : "Collapse"}</span>
            </Button>
            
            {lastUpdated && <span className="text-[10px] text-muted-foreground">Updated {lastUpdated.toLocaleTimeString()}</span>}
          </div>
        </CardContent>
      </Card>

      {/* FIX: Conditional Rendering - Table completely disappears when collapsed */}
      {isCollapsed ? (
        <div className="flex-1 flex items-center justify-center border border-dashed rounded-md bg-muted/20 min-h-[200px]">
          <div className="text-center text-muted-foreground">
            <p className="text-sm font-semibold mb-1">Asset List Collapsed</p>
            <p className="text-xs">Space reserved for Signals & Analytics</p>
          </div>
        </div>
      ) : (
        <Card className="flex-1 min-h-0 overflow-hidden flex flex-col">
          <CardHeader className="!pb-2 shrink-0">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{data?.exchange || "Hyperliquid"} Assets ({data?.total})</span>
            </div>
          </CardHeader>
          <CardContent className="flex-1 min-h-0 p-0 overflow-hidden">
            <div className="h-full overflow-auto">
              <table className="w-full text-xs">
                <thead className="sticky top-0 bg-card z-10">
                  <tr className="text-left text-[10px] uppercase tracking-wider text-muted-foreground border-b border-border">
                    <th className="py-2 px-3 font-normal w-12">#</th>
                    <th className="py-2 px-3 font-normal">Asset</th>
                    <th className="py-2 px-3 font-normal">Category</th>
                    <th 
  className="py-2 px-3 font-normal text-right cursor-pointer hover:text-foreground transition-colors"
  onClick={() => {
    if (sortKey === 'volume_24h') {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey('volume_24h')
      setSortOrder('desc')
    }
  }}
  title="Sort by 24h Volume"
>
  Volume (24h){sortKey === 'volume_24h' && <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>}
</th>
                    <th className="py-2 px-3 font-normal text-right">Price</th>
                    <th 
  className="py-2 px-3 font-normal text-right cursor-pointer hover:text-foreground transition-colors"
  onClick={() => {
    if (sortKey === 'change_24h') {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey('change_24h')
      setSortOrder('desc')
    }
  }}
  title="Sort by 24h Price Change"
>
  24h Change{sortKey === 'change_24h' && <span className="ml-1">{sortOrder === 'asc' ? '↑' : '↓'}</span>}
</th>
                    <th className="py-2 px-3 font-normal">24h Trend</th>
                    <th className="py-2 px-3 font-normal">Market Regime</th>
                    <th className="py-2 px-3 font-normal">Correlation</th>
                    <th className="py-2 px-3 font-normal text-right">Max Lev</th>
                  </tr>
                </thead>
                <tbody className="font-mono">
                  {sortedAssets?.map((a: AssetData, index: number) => {
                    const symbol = a.symbol || a.name
                    const change24h = a.change_24h
                    const changeColor = change24h !== undefined ? (change24h >= 0 ? "text-long" : "text-short") : "text-muted-foreground"
                    const livePrice = livePrices[symbol]
                    const displayPrice = livePrice ? parseFloat(livePrice) : a.price
                    
                    return (
                      <tr key={`${a.exchange || 'HL'}-${symbol}`} className="border-b border-border last:border-0 hover:bg-secondary/50 cursor-pointer transition-colors" onClick={() => onTradeAsset?.(symbol)}>
                        <td className="py-2 px-3 text-muted-foreground">{a.rank || index + 1}</td>
                        <td className="py-2 px-3 font-sans font-semibold flex items-center gap-2">
                          {a.logo_url ? (
                            <img src={a.logo_url} onError={(e) => handleImageError(e, symbol)} className="w-6 h-6 rounded-full object-cover bg-gray-900 border border-gray-800 shrink-0" alt={symbol} />
                          ) : (
                            <div className="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 flex items-center justify-center text-[10px] font-bold shrink-0 border border-blue-500/30">{symbol.slice(0, 2).toUpperCase()}</div>
                          )}
                          <span>{symbol}</span>
                        </td>
                        <td className="py-2 px-3"><Badge className="text-[10px]">{a.category}</Badge></td>
                        <td className="py-2 px-3 text-right">${a.volume_24h.toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                        <td className={cn("py-2 px-3 text-right font-semibold", livePrice ? "text-primary" : "")}>
                          {displayPrice ? `$${displayPrice.toLocaleString()}` : "—"}
                          {livePrice && <span className="ml-1 text-[10px] text-muted-foreground">●</span>}
                        </td>
                        <td className={cn("py-2 px-3 text-right font-semibold", changeColor)}>
                          {change24h !== undefined ? `${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%` : "—"}
                        </td>
                        <td className="py-2 px-3">
                          {a.sparkline && a.sparkline.length > 0 ? <Sparkline data={a.sparkline} width={80} height={30} /> : <div className="w-20 h-8 flex items-center justify-center text-[10px] text-muted-foreground">—</div>}
                        </td>
                        <td className="py-2 px-3">{regimeBadge(a.regime)}</td>
                        <td className="py-2 px-3">{correlationBadge(a.correlation_group)}</td>
                        <td className="py-2 px-3 text-right">{a.max_leverage}x</td>
                      </tr>
                    )
                  })}
                  {data?.assets.length === 0 && <tr><td colSpan={10} className="py-8 text-center text-muted-foreground">No assets match your filters.</td></tr>}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
