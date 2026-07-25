import { useEffect, useRef, useState, useCallback } from "react"
import { 
  createChart, 
  CandlestickSeries, 
  HistogramSeries, 
  CrosshairMode, 
  LineStyle,
  type IChartApi, 
  type ISeriesApi, 
  type UTCTimestamp 
} from "lightweight-charts"
import { apiFetch } from "@/lib/api"
import { cn } from "@/lib/utils"
import { RefreshCw } from "lucide-react"

interface RawHlCandle {
  t: number
  T: number
  s: string
  i: string
  o: string
  c: string
  h: string
  l: string
  v: string
  n: number
}

interface AssetData {
  name: string
  symbol?: string
  volume_24h: number
  price: number
  change_24h: number
}

const INTERVALS = ["1m", "5m", "15m", "1h", "4h", "1d", "3d", "1w", "1M"] as const
type Interval = typeof INTERVALS[number]

export function CandleChart() {
  const [asset, setAsset] = useState("BTC")
  const [interval, setInterval_] = useState<Interval>("1h")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [assets, setAssets] = useState<AssetData[]>([])
  const [currentPrice, setCurrentPrice] = useState<number | null>(null)
  const [priceChange, setPriceChange] = useState<number | null>(null)

  const containerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null)

  // Step 1: Fetch top assets for dropdown
  const fetchAssets = useCallback(async () => {
    try {
      const res = await apiFetch<{ assets: AssetData[] }>("/assets/universe")
      if (res.assets && res.assets.length > 0) {
        // Sort by volume and take top 30
        const sorted = [...res.assets].sort((a, b) => b.volume_24h - a.volume_24h).slice(0, 30)
        setAssets(sorted)
      }
    } catch (e) {
      console.error("Failed to fetch assets for dropdown:", e)
    }
  }, [])

  // Step 2: Initialize chart with volume bars
  useEffect(() => {
    if (!containerRef.current) return
    
    const chart = createChart(containerRef.current, {
      layout: { 
        background: { color: "transparent" }, 
        textColor: "#94a3b8",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "rgba(148, 163, 184, 0.05)", style: LineStyle.Dotted },
        horzLines: { color: "rgba(148, 163, 184, 0.05)", style: LineStyle.Dotted },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: "rgba(148, 163, 184, 0.4)", style: LineStyle.Dashed, labelBackgroundColor: "#475569" },
        horzLine: { color: "rgba(148, 163, 184, 0.4)", style: LineStyle.Dashed, labelBackgroundColor: "#475569" },
      },
      timeScale: { 
        timeVisible: true, 
        secondsVisible: false,
        borderColor: "rgba(148, 163, 184, 0.1)",
      },
      rightPriceScale: {
        borderColor: "rgba(148, 163, 184, 0.1)",
      },
      autoSize: true,
    })

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e", 
      downColor: "#ef4444",
      borderUpColor: "#22c55e", 
      borderDownColor: "#ef4444",
      wickUpColor: "#22c55e", 
      wickDownColor: "#ef4444",
    })

    // Step 3: Add volume bars at bottom
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
    })
    
    // Configure volume scale margins (bottom 20% of chart)
    chart.priceScale("").applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    })

    chartRef.current = chart
    candleSeriesRef.current = candleSeries
    volumeSeriesRef.current = volumeSeries

    const resizeObserver = new ResizeObserver(() => chart.applyOptions({}))
    resizeObserver.observe(containerRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.remove()
      chartRef.current = null
      candleSeriesRef.current = null
      volumeSeriesRef.current = null
    }
  }, [])

  // Step 4: Fetch candles with volume data
  const fetchCandles = useCallback(async () => {
    setLoading(true)
    try {
      const raw = await apiFetch<RawHlCandle[]>("/terminal/candles", {
        method: "POST",
        body: JSON.stringify({ coin: asset, interval }),
      })
      
      if (!Array.isArray(raw) || raw.length === 0) {
        setError("No candle data returned")
        return
      }

      const candleData = raw.map((c) => ({
        time: Math.floor(c.t / 1000) as UTCTimestamp,
        open: parseFloat(c.o),
        high: parseFloat(c.h),
        low: parseFloat(c.l),
        close: parseFloat(c.c),
      })).sort((a, b) => a.time - b.time)

      // Step 5: Create volume data with color coding
      const volumeData = raw.map((c) => ({
        time: Math.floor(c.t / 1000) as UTCTimestamp,
        value: parseFloat(c.v),
        color: parseFloat(c.c) >= parseFloat(c.o) ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)",
      })).sort((a, b) => a.time - b.time)

      candleSeriesRef.current?.setData(candleData)
      volumeSeriesRef.current?.setData(volumeData)
      chartRef.current?.timeScale().fitContent()
      
      // Step 6: Update price display from last candle
      const lastCandle = candleData[candleData.length - 1]
      const firstCandle = candleData[0]
      if (lastCandle && firstCandle) {
        setCurrentPrice(lastCandle.close)
        const change = ((lastCandle.close - firstCandle.open) / firstCandle.open) * 100
        setPriceChange(change)
      }
      
      setError(null)
    } catch {
      setError("Failed to load candles")
    } finally {
      setLoading(false)
    }
  }, [asset, interval])

  // Fetch assets on mount
  useEffect(() => {
    fetchAssets()
  }, [fetchAssets])

  // Step 7: Auto-refresh every 30 seconds
  useEffect(() => {
    fetchCandles()
    
    if (!autoRefresh) return
    
    const intervalId = setInterval(fetchCandles, 30000)
    return () => clearInterval(intervalId)
  }, [fetchCandles, autoRefresh])

  const priceColor = priceChange !== null ? (priceChange >= 0 ? "text-[#22c55e]" : "text-[#ef4444]") : "text-muted-foreground"
  const priceSign = priceChange !== null && priceChange > 0 ? "+" : ""

  return (
    <div className="flex h-full flex-col">
      {/* Header Controls */}
      <div className="mb-2 flex items-center gap-3 flex-wrap">
        {/* Step 1: Asset Selector Dropdown */}
        <select
          value={asset}
          onChange={(e) => setAsset(e.target.value)}
          className="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs font-mono outline-none focus:ring-1 focus:ring-primary"
        >
          {assets.length === 0 && <option value={asset}>{asset}</option>}
          {assets.map((a) => (
            <option key={a.name} value={a.name}>
              {a.name}
            </option>
          ))}
        </select>

        {/* Step 2: Timeframe Buttons */}
        <div className="flex gap-1">
          {INTERVALS.map((iv) => (
            <button
              key={iv}
              onClick={() => setInterval_(iv)}
              className={cn(
                "rounded-md px-2.5 py-1 text-xs font-mono transition-colors",
                interval === iv ? "bg-primary/15 text-primary font-semibold" : "bg-secondary text-muted-foreground hover:bg-secondary/80"
              )}
            >
              {iv}
            </button>
          ))}
        </div>

        {/* Step 5: Price Display with Change Indicator */}
        {currentPrice !== null && (
          <div className="ml-auto flex items-baseline gap-2">
            <span className="text-lg font-bold font-mono text-foreground">
              ${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            {priceChange !== null && (
              <span className={cn("text-xs font-mono font-semibold", priceColor)}>
                {priceSign}{priceChange.toFixed(2)}%
              </span>
            )}
          </div>
        )}

        {/* Step 6: Auto-refresh Toggle */}
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={cn(
            "flex items-center gap-1.5 rounded-md px-2 py-1 text-xs transition-colors",
            autoRefresh ? "bg-primary/10 text-primary" : "bg-secondary text-muted-foreground"
          )}
          title={autoRefresh ? "Auto-refresh ON (30s)" : "Auto-refresh OFF"}
        >
          <RefreshCw className={cn("h-3 w-3", autoRefresh && "animate-spin", loading && "animate-spin")} />
          <span className="hidden sm:inline">Auto</span>
        </button>

        {error && <span className="text-xs text-destructive">{error}</span>}
      </div>

      {/* Chart Container */}
      <div ref={containerRef} className="min-h-0 flex-1 rounded-md border border-border bg-card/50" />
    </div>
  )
}
