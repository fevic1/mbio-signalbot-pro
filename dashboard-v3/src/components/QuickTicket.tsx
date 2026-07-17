import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { apiFetch } from "@/lib/api"
import { TrendingUp, TrendingDown, Bot } from "lucide-react"

interface QuickTicketProps {
  initialAsset?: string
  onClose?: () => void
}

export function QuickTicket({ initialAsset, onClose }: QuickTicketProps) {
  const [side, setSide] = useState<"BUY" | "SELL">("BUY")
  const [orderType, setOrderType] = useState<"market" | "limit">("market")
  const [asset, setAsset] = useState(initialAsset || "BTC")
  const [sizeUsd, setSizeUsd] = useState("")
  const [limitPx, setLimitPx] = useState("")
  const [sl, setSl] = useState("")
  const [tp, setTp] = useState("")
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  // Update asset when initialAsset changes
  useEffect(() => {
    if (initialAsset) {
      setAsset(initialAsset)
    }
  }, [initialAsset])

  const submit = async () => {
    if (!sizeUsd || !otp) {
      alert("Size and OTP code are required")
      return
    }
    if (orderType === "limit" && !limitPx) {
      alert("Limit price is required for limit orders")
      return
    }

    setSubmitting(true)
    try {
      const body: Record<string, any> = {
        asset,
        side,
        type: orderType,
        size_usd: parseFloat(sizeUsd),
        otp,
      }
      if (orderType === "limit") body.limit_px = parseFloat(limitPx)
      if (sl) body.sl = parseFloat(sl)
      if (tp) body.tp = parseFloat(tp)

      await apiFetch("/open_order", {
        method: "POST",
        body: JSON.stringify(body),
      })
      
      alert("Order submitted successfully")
      setSizeUsd("")
      setLimitPx("")
      setSl("")
      setTp("")
      setOtp("")
    } catch (e: any) {
      alert(e.message || "Order failed")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card className="w-80 h-full flex flex-col border-none shadow-none">
      <CardHeader className="!pb-2 shrink-0">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold">Quick Ticket</span>
          {onClose && (
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
              X
            </button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-y-auto space-y-3">
        {/* Side Buttons */}
        <div className="flex gap-2">
          <button
            onClick={() => setSide("BUY")}
            className={cn(
              "flex-1 rounded-md py-2 text-sm font-semibold capitalize transition-colors flex items-center justify-center gap-1.5",
              side === "BUY" 
                ? "bg-long text-background shadow-lg shadow-long/20" 
                : "bg-secondary text-muted-foreground hover:bg-secondary/80"
            )}
          >
            <TrendingUp className="h-4 w-4" />
            Buy
          </button>
          <button
            onClick={() => setSide("SELL")}
            className={cn(
              "flex-1 rounded-md py-2 text-sm font-semibold capitalize transition-colors flex items-center justify-center gap-1.5",
              side === "SELL" 
                ? "bg-short text-background shadow-lg shadow-short/20" 
                : "bg-secondary text-muted-foreground hover:bg-secondary/80"
            )}
          >
            <TrendingDown className="h-4 w-4" />
            Sell
          </button>
        </div>

        {/* Order Type */}
        <div className="flex gap-2">
          {(["market", "limit"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setOrderType(t)}
              className={cn(
                "flex-1 rounded-md py-1.5 text-xs font-semibold capitalize transition-colors",
                orderType === t ? "bg-primary/15 text-primary" : "bg-secondary text-muted-foreground"
              )}
            >
              {t}
            </button>
          ))}
        </div>

        {/* Asset Input */}
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
            Asset
          </label>
          <input
            value={asset}
            onChange={(e) => setAsset(e.target.value.toUpperCase())}
            className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-primary"
            placeholder="BTC"
          />
        </div>

        {/* Size Input */}
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
            Size (USD)
          </label>
          <input
            value={sizeUsd}
            onChange={(e) => setSizeUsd(e.target.value)}
            placeholder="0.00"
            className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Limit Price (for limit orders) */}
        {orderType === "limit" && (
          <div>
            <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
              Limit Price
            </label>
            <input
              value={limitPx}
              onChange={(e) => setLimitPx(e.target.value)}
              placeholder="0.00"
              className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        )}

        {/* Advanced: Stop Loss */}
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
            Stop Loss (Optional)
          </label>
          <input
            value={sl}
            onChange={(e) => setSl(e.target.value)}
            placeholder="0.00"
            className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-warn"
          />
        </div>

        {/* Advanced: Take Profit */}
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
            Take Profit (Optional)
          </label>
          <input
            value={tp}
            onChange={(e) => setTp(e.target.value)}
            placeholder="0.00"
            className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-long"
          />
        </div>

        {/* OTP */}
        <div>
          <label className="mb-1 block text-xs uppercase tracking-wider text-muted-foreground">
            OTP Code
          </label>
          <input
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit code"
            maxLength={6}
            className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {/* Submit Button */}
        <Button
          className="w-full mt-2"
          onClick={submit}
          disabled={submitting}
        >
          {submitting ? "Submitting…" : "Place market order"}
        </Button>

        {/* Create Bot Button */}
        <div className="border-t border-border pt-3 mt-2">
          <Button variant="outline" className="w-full flex items-center justify-center gap-2">
            <Bot className="h-4 w-4" />
            + Create Bot
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
