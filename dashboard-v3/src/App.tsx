import { useEffect, useState } from "react"
import {
  LayoutDashboard, Grid3x3, TrendingUp, ListOrdered, Radio, Settings,
  ShieldAlert, AlertTriangle, Check, X, LogOut, ChevronLeft, ChevronRight,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { useAuth } from "@/store/auth"
import { Login } from "@/components/Login"
import { apiFetch, ApiError } from "@/lib/api"
import { OverviewPanel } from "@/components/OverviewPanel"
import { PositionsPanel } from "@/components/PositionsPanel"
import { ActivityPanel } from "@/components/ActivityPanel"
import { OrdersPanel } from "@/components/OrdersPanel"
import { OpenGridForm } from "@/components/OpenGridForm"
import { OpenDcaForm } from "@/components/OpenDcaForm"
import { MetaLearnerPanel } from "@/components/MetaLearnerPanel"
import { CandleChart } from "@/components/CandleChart"
import { BotsMiniList } from "@/components/BotsMiniList"
import { AssetUniversePanel } from "@/components/AssetUniversePanel"
import { AiosRuntimePanel } from "@/components/AiosRuntimePanel"

type MonitorStatus = { id: string; label: string; status: "ok" | "warn"; detail?: string; }

function useHealthMonitors() {
  const [monitors, setMonitors] = useState<MonitorStatus[]>([
    { id: "position_monitor", label: "position monitor", status: "ok" },
    { id: "quick_scanner", label: "quick scanner", status: "ok" },
    { id: "entry_scanner", label: "entry scanner", status: "ok" },
    { id: "full_analysis", label: "full analysis", status: "ok" },
    { id: "slot_hunter", label: "slot hunter", status: "warn", detail: "Task registered but returns immediately — confirmed dead stub, not a live outage." },
    { id: "trailing_dca", label: "trailing dca", status: "ok" },
    { id: "profit_target_monitor", label: "profit target monitor", status: "ok" },
    { id: "grid_monitor", label: "grid monitor", status: "ok" },
  ]);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await apiFetch<any>("/system/status");
        if (res && res.tasks) {
          setMonitors(prev => prev.map(h => {
            const task = res.tasks.find((t: any) => t.name === h.id || t.id === h.id);
            if (task) {
              return { ...h, status: (task.status === "running" || task.status === "active") ? "ok" : "warn" } as MonitorStatus;
            }
            return h;
          }));
        }
      } catch (e) { /* ignore fetch errors */ }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return monitors;
}

const NAV = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "assets", label: "Assets", icon: Grid3x3 },
  { id: "bots", label: "Grid Bots", icon: Grid3x3 },
  { id: "positions", label: "Positions", icon: TrendingUp },
  { id: "orders", label: "Orders", icon: ListOrdered },
  { id: "signals", label: "Activity", icon: Radio },
  { id: "settings", label: "Settings", icon: Settings },
] as const

type TabId = typeof NAV[number]["id"]

type TicketContext =
  | { type: "edit_bot"; coin: string }
  | { type: "close_position"; asset: string; side: string; size: number }
  | { type: "close_grid"; asset: string }
  | { type: "open_grid" }
  | { type: "close_dca"; asset: string }
  | { type: "quick_trade"; asset: string; side?: "BUY" | "SELL" }
  | { type: "open_dca" }
  | { type: "create_bot_choice" }
  | { type: "quick" }
  | null

function QuickOrderForm({ onResult, onSuccess, initialAsset, initialSide }: { onResult: (msg: string, isError: boolean) => void; onSuccess?: () => void; initialAsset?: string; initialSide?: "BUY" | "SELL" }) {
  const [side, setSide] = useState<"BUY" | "SELL">(initialSide || "BUY")
  const [orderType, setOrderType] = useState<"market" | "limit">("market")
  const [asset, setAsset] = useState(initialAsset || "BTC")
  const [sizeUsd, setSizeUsd] = useState("")
  const [limitPx, setLimitPx] = useState("")
  const [sl, setSl] = useState("")
  const [tp, setTp] = useState("")
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!sizeUsd || !otp) {
      onResult("Size and OTP code are required", true)
      return
    }
    if (orderType === "limit" && !limitPx) {
      onResult("Limit price is required for limit orders", true)
      return
    }
    setSubmitting(true)
    try {
      const body: Record<string, unknown> = {
        asset,
        side,
        type: orderType,
        size_usd: parseFloat(sizeUsd),
        otp,
      }
      if (orderType === "limit") body.limit_px = parseFloat(limitPx)
      if (sl) body.sl = parseFloat(sl)
      if (tp) body.tp = parseFloat(tp)

      const result = await apiFetch<{ status: string; message: string }>("/open_order", {
        method: "POST",
        body: JSON.stringify(body),
      })
      onResult(result.message || "Order submitted", false)
      if (onSuccess) onSuccess()
      setSizeUsd("")
      setLimitPx("")
      setSl("")
      setTp("")
      setOtp("")
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Order failed"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="flex gap-2">
        {(["BUY", "SELL"] as const).map((s) => (
          <button
            key={s}
            onClick={() => setSide(s)}
            className={cn(
              "flex-1 rounded-md py-2 text-sm font-semibold capitalize transition-colors",
              side === s ? (s === "BUY" ? "bg-long text-background" : "bg-short text-background") : "bg-secondary text-muted-foreground"
            )}
          >
            {s === "BUY" ? "Buy" : "Sell"}
          </button>
        ))}
      </div>
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
            {t === "market" ? "Market" : "Limit"}
          </button>
        ))}
      </div>
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">Asset</span>
        <input value={asset} onChange={(e) => setAsset(e.target.value.toUpperCase())} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">Size (USD)</span>
        <input value={sizeUsd} onChange={(e) => setSizeUsd(e.target.value)} placeholder="0.00" className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      {orderType === "limit" && (
        <label className="block text-xs">
          <span className="mb-1 block uppercase tracking-wider text-muted-foreground">Limit price</span>
          <input value={limitPx} onChange={(e) => setLimitPx(e.target.value)} placeholder="0.00" className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
        </label>
      )}
      <div className="grid grid-cols-2 gap-2">
        <label className="block text-xs">
          <span className="mb-1 block uppercase tracking-wider text-muted-foreground">SL (optional)</span>
          <input value={sl} onChange={(e) => setSl(e.target.value)} placeholder="0.00" className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
        </label>
        <label className="block text-xs">
          <span className="mb-1 block uppercase tracking-wider text-muted-foreground">TP (optional)</span>
          <input value={tp} onChange={(e) => setTp(e.target.value)} placeholder="0.00" className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
        </label>
      </div>
      {(sl || tp) && (
        <div className="rounded-md border border-warn/40 bg-warn/10 p-2 text-[11px] text-warn">
          SL/TP here are bot-monitored, not real exchange orders — the position monitor checks
          price every ~60s and market-closes if crossed. A fast move between checks can slip past
          the level. Not a substitute for an exchange-native stop.
        </div>
      )}
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">OTP code</span>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      <Button className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Submitting…" : `Place ${orderType} order`}
      </Button>
    </>
  )
}

function CloseGridForm({ asset, onResult, onSuccess, triggerRefresh }: { asset: string; onResult: (msg: string, isError: boolean) => void; onSuccess?: () => void; triggerRefresh?: () => void }) {
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!otp) {
      onResult("OTP code is required", true)
      return
    }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/grid/close", {
        method: "POST",
        body: JSON.stringify({ asset, otp }),
      })
      onResult(result.message || "Grid closed", false)
      if (onSuccess) onSuccess()
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Grid close failed"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="rounded-md border border-warn/40 bg-warn/10 p-3 text-xs text-warn">
        This cancels all open grid orders for {asset} and closes any resulting position. This is
        a destructive action — the grid's node history and cycle count for this session will not
        be recoverable after closing.
      </div>
      <div className="text-xs font-mono text-muted-foreground">Closing grid: {asset}</div>
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">OTP code</span>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      <Button variant="destructive" className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Closing…" : `Close ${asset} grid`}
      </Button>
    </>
  )
}

function CloseDcaForm({ asset, onResult, onSuccess, triggerRefresh }: { asset: string; onResult: (msg: string, isError: boolean) => void; onSuccess?: () => void; triggerRefresh?: () => void }) {
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!otp) {
      onResult("OTP code is required", true)
      return
    }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/dca/close", {
        method: "POST",
        body: JSON.stringify({ asset, otp }),
      })
      onResult(result.message || "DCA position closed", false)
      if (onSuccess) onSuccess()
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "DCA close failed"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="rounded-md border border-warn/40 bg-warn/10 p-3 text-xs text-warn">
        Cancels all active DCA safety orders for {asset} and closes any resulting position at
        market. This is destructive — level/fill history for this DCA cycle will not be
        recoverable after closing.
      </div>
      <div className="text-xs font-mono text-muted-foreground">Closing DCA: {asset}</div>
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">OTP code</span>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      <Button variant="destructive" className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Closing…" : `Close ${asset} DCA`}
      </Button>
    </>
  )
}

function ClosePositionForm({ asset, side, size, onResult, onSuccess, triggerRefresh }: { asset: string; side: string; size: number; onResult: (msg: string, isError: boolean) => void; onSuccess?: () => void; triggerRefresh?: () => void }) {
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!otp) {
      onResult("OTP code is required", true)
      return
    }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/close", {
        method: "POST",
        body: JSON.stringify({ asset, otp }),
      })
      onResult(result.message || "Position closed", false)
      if (onSuccess) onSuccess()
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Close failed"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <>
      <div className="rounded-md border border-border bg-secondary/50 p-3 text-xs text-muted-foreground">
        Closes the entire {asset} position via a reduce-only market order. The backend fetches
        the live position size directly from the exchange at execution time, not the size shown
        here — so this stays accurate even if the position changed since this panel last refreshed.
      </div>
      <div className="text-xs font-mono text-muted-foreground">
        {asset} · currently {side === "BUY" ? "Long" : "Short"} {size}
      </div>
      <label className="block text-xs">
        <span className="mb-1 block uppercase tracking-wider text-muted-foreground">OTP code</span>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className="w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none" />
      </label>
      <Button variant="destructive" className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Closing…" : `Close ${asset} position`}
      </Button>
    </>
  )
}

function Ticket({ context, onClose, onResult, triggerRefresh, triggerGridRefresh, onChooseBotType, onCreateBot, botsListProps }: { 
  context: TicketContext; 
  onClose: () => void; 
  onResult: (msg: string, isError: boolean) => void; 
  triggerRefresh?: () => void; 
  triggerGridRefresh?: () => void; 
  onChooseBotType?: (t: "grid" | "dca") => void; 
  onCreateBot?: () => void; 
  botsListProps?: { onCloseGrid: (asset: string) => void; onCloseDca: (asset: string) => void; refreshKey: number } 
}) {
  const handleSuccess = () => {
    onClose()
  }

  return (
    <div className="flex h-full flex-col border-l border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <span className="text-sm font-semibold">
          {context?.type === "edit_bot" ? `Edit — ${context.coin}` : 
           context?.type === "open_grid" ? "Open Grid Bot" :
           context?.type === "open_dca" ? "Open DCA Position" :
           context?.type === "close_grid" ? `Close ${context.asset} Grid` :
           context?.type === "close_dca" ? `Close ${context.asset} DCA` :
           context?.type === "close_position" ? `Close ${context.asset} Position` :
           context?.type === "create_bot_choice" ? "Create Bot" :
           "Quick Ticket"}
        </span>
        {context && (
          <Button size="icon" variant="ghost" onClick={onClose}><X className="h-3.5 w-3.5" /></Button>
        )}
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {context?.type === "open_grid" ? (
          <OpenGridForm onResult={onResult} onSuccess={handleSuccess} triggerRefresh={triggerGridRefresh} />
        ) : context?.type === "open_dca" ? (
          <OpenDcaForm onResult={onResult} onSuccess={handleSuccess} triggerRefresh={triggerGridRefresh} />
        ) : context?.type === "close_position" ? (
          <ClosePositionForm asset={context.asset} side={context.side} size={context.size} onResult={onResult} onSuccess={handleSuccess} triggerRefresh={triggerRefresh} />
        ) : context?.type === "close_grid" ? (
          <CloseGridForm asset={context.asset} onResult={onResult} onSuccess={handleSuccess} triggerRefresh={triggerGridRefresh} />
        ) : context?.type === "close_dca" ? (
          <CloseDcaForm asset={context.asset} onResult={onResult} onSuccess={handleSuccess} triggerRefresh={triggerGridRefresh} />
        ) : context?.type === "edit_bot" ? (
          <div className="rounded-md border border-warn/40 bg-warn/10 p-3 text-xs text-warn">
            No "edit range" endpoint exists yet on the backend — only grid open and grid close.
            Adjusting range currently requires closing and reopening the grid, which is a
            different operation with different risk (loses current node fills/state). Not
            wiring this until a real update endpoint exists.
          </div>
        ) : context?.type === "create_bot_choice" ? (
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
            Select a bot type below to begin.
          </div>
        ) : (
          <>
            <QuickOrderForm onResult={onResult} onSuccess={handleSuccess} />
            {botsListProps && (
              <div className="border-t border-border pt-4 mt-4">
                <BotsMiniList {...botsListProps} />
              </div>
            )}
          </>
        )}
      </div>
      <div className="border-t border-border p-4 space-y-2">
        {context?.type === "create_bot_choice" ? (
          <>
            <Button className="w-full" onClick={() => onChooseBotType?.("grid")}>Grid Bot</Button>
            <Button className="w-full" onClick={() => onChooseBotType?.("dca")}>DCA Position</Button>
          </>
        ) : context?.type === "quick_trade" ? (
          <QuickOrderForm 
            initialAsset={context.asset} 
            initialSide={context.side}
            onResult={onResult} 
            onSuccess={handleSuccess} 
          />
        ) : context && context.type !== "quick" ? (
          <Button variant="outline" className="w-full" onClick={onClose}>← Back to Quick Ticket</Button>
        ) : (
          <Button onClick={onCreateBot} className="w-full">+ Create Bot</Button>
        )}
      </div>
    </div>
  )
}

function HealthBar({ selected, onSelect }: { selected: string | null; onSelect: (id: string | null) => void }) {
  const healthMonitors = useHealthMonitors();
  const detail = healthMonitors.find((h) => h.id === selected)
  return (
    <div className="border-t border-border">
      <div className="flex flex-wrap items-center gap-2 bg-card px-4 py-2">
        <ShieldAlert className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        {healthMonitors.map((h) => {
          const ok = h.status === "ok"
          return (
            <button
              key={h.id}
              onClick={() => onSelect(ok ? null : h.id)}
              className={cn(
                "flex shrink-0 items-center gap-1.5 rounded-md px-2 py-1 text-xs transition-colors",
                ok ? "text-muted-foreground" : "text-warn",
                selected === h.id && "bg-warn/15"
              )}
            >
              {ok ? <Check className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
              {h.label}
            </button>
          )
        })}
      </div>
      {detail && (
        <div className="border-t border-border bg-warn/10 px-4 py-2 text-xs text-warn">
          <strong>{detail.label}:</strong> {detail.detail}
        </div>
      )}
    </div>
  )
}

function Dashboard() {
  const { user, logout } = useAuth()
  const [tab, setTab] = useState<TabId>("bots")
  const [ticketCtx, setTicketCtx] = useState<TicketContext>(null)
  const [selectedHealth, setSelectedHealth] = useState<string | null>(null)
  const [positionRefreshKey, setPositionRefreshKey] = useState(0)
  const triggerPositionRefresh = () => setPositionRefreshKey(prev => prev + 1)
  const [gridRefreshKey, setGridRefreshKey] = useState(0)
  const triggerGridRefresh = () => setGridRefreshKey(prev => prev + 1)
  const [navExpanded, setNavExpanded] = useState(false)
  const [ticketExpanded, setTicketExpanded] = useState(true)
  const [toast, setToast] = useState<{ msg: string; isError: boolean } | null>(null)
  const [confirmStop, setConfirmStop] = useState(false)
  
  // FIX: Call the hook at the top level of the component
  const healthMonitors = useHealthMonitors();
  
  const notify = (msg: string, isError = false) => {
    setToast({ msg, isError })
    setTimeout(() => setToast(null), 3500)
  }

  return (
    <div className="flex h-screen w-full flex-col bg-background text-foreground">
      <div className="flex items-center justify-between border-b border-border bg-card px-4 py-3">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold">MBIO</span>
          <span className="flex items-center gap-1.5 text-xs font-mono text-muted-foreground">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-long" /> LIVE
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{user?.email} · {user?.role}</span>
          <Button variant="ghost" size="icon" onClick={() => logout()} title="Sign out">
            <LogOut className="h-3.5 w-3.5" />
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setConfirmStop(true)}>
            <AlertTriangle className="h-3.5 w-3.5" /> EMERGENCY STOP
          </Button>
        </div>
      </div>

      <div className="flex min-h-0 flex-1">
        <div className={cn(
          "flex shrink-0 flex-col gap-1 border-r border-border bg-card py-3 transition-all",
          navExpanded ? "w-40 items-stretch px-2" : "w-14 items-center"
        )}>
          {NAV.map((n) => {
            const Icon = n.icon
            const active = tab === n.id
            return (
              <Button
                key={n.id}
                variant="ghost"
                title={n.label}
                onClick={() => setTab(n.id)}
                className={cn(
                  active && "bg-primary/15 text-primary",
                  navExpanded ? "justify-start gap-2 px-2" : "w-9 justify-center px-0"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {navExpanded && <span className="text-xs">{n.label}</span>}
              </Button>
            )
          })}
          <Button
            variant="ghost"
            onClick={() => setNavExpanded((v) => !v)}
            title={navExpanded ? "Collapse" : "Expand"}
            className={navExpanded ? "justify-start gap-2 px-2" : "w-9 justify-center px-0"}
          >
            {navExpanded ? <ChevronLeft className="h-4 w-4 shrink-0" /> : <ChevronRight className="h-4 w-4 shrink-0" />}
            {navExpanded && <span className="text-xs">Collapse</span>}
          </Button>
          <Button
            variant="ghost"
            className={cn("mt-auto", navExpanded ? "justify-start gap-2 px-2" : "w-9 justify-center px-0")}
            title="Settings"
          >
            <Settings className="h-4 w-4 shrink-0" />
            {navExpanded && <span className="text-xs">Settings</span>}
          </Button>
        </div>

        <div className="flex min-w-0 flex-1 flex-col">
          <div className="flex-1 overflow-y-auto p-4">
            {tab === "bots" && (
              <div className="flex h-full min-h-0">
                <div className="flex min-w-0 flex-1 flex-col gap-3">
                  <div className="h-[420px] shrink-0 rounded-md border border-border bg-card p-3">
                    <CandleChart />
                  </div>
                  <div className="min-h-0 flex-1 overflow-y-auto">
                    <div className="mb-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Open Trades
                    </div>
                    <PositionsPanel
                      onClose={(pos) => setTicketCtx({ type: "close_position", asset: pos.asset, side: pos.side, size: pos.size })}
                      refreshKey={positionRefreshKey}
                    />
                  </div>
                </div>
              </div>
            )}
            {tab === "overview" && <div className="space-y-4">
              <OverviewPanel />
              <AiosRuntimePanel />
              <MetaLearnerPanel />
            </div>}
            {tab === "assets" && <AssetUniversePanel onTradeAsset={(asset, side) => setTicketCtx({ type: "quick_trade", asset, side })} />}
            {tab === "positions" && (
              <PositionsPanel onClose={(pos) => setTicketCtx({ type: "close_position", asset: pos.asset, side: pos.side, size: pos.size })} refreshKey={positionRefreshKey} />
            )}
            {tab === "orders" && <OrdersPanel />}
            {tab === "signals" && <ActivityPanel />}
            {tab === "settings" && (
              <Card>
                <CardHeader><h2 className="text-lg font-semibold">Monitor Settings</h2></CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {healthMonitors.map((h) => (
                      <div key={h.id} className="flex items-center justify-between border-b border-border pb-2">
                        <div>
                          <p className="font-medium capitalize">{h.label.replace(/_/g, ' ')}</p>
                          <p className="text-xs text-muted-foreground">Status: {h.status === 'ok' ? 'Active' : 'Warning'}</p>
                        </div>
                        <button className={`px-3 py-1 rounded text-xs ${h.status === 'ok' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'}`}>
                          {h.status === 'ok' ? 'Enabled' : 'Review'}
                        </button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
          <HealthBar selected={selectedHealth} onSelect={setSelectedHealth} />
        </div>

        <div className="flex shrink-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTicketExpanded((v) => !v)}
            title={ticketExpanded ? "Collapse ticket" : "Expand ticket"}
            className="h-auto self-stretch rounded-none border-l border-border px-1"
          >
            {ticketExpanded ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
          {ticketExpanded && (
            <div className="w-80 shrink-0">
              <Ticket
                context={ticketCtx}
                onClose={() => setTicketCtx(null)}
                onResult={(msg, isError) => {
                  notify(msg, isError)
                  if (!isError) setTicketCtx(null)
                }}
                triggerRefresh={triggerPositionRefresh}
                triggerGridRefresh={triggerGridRefresh}
                onChooseBotType={(t) => setTicketCtx(t === "grid" ? { type: "open_grid" } : { type: "open_dca" })}
                onCreateBot={() => setTicketCtx({ type: "create_bot_choice" })}
                botsListProps={{
                  onCloseGrid: (asset) => setTicketCtx({ type: "close_grid", asset }),
                  onCloseDca: (asset) => setTicketCtx({ type: "close_dca", asset }),
                  refreshKey: gridRefreshKey
                }}
              />
            </div>
          )}
        </div>
      </div>

      {toast && (
        <div className={cn(
          "absolute bottom-4 left-1/2 -translate-x-1/2 rounded-md border px-4 py-2 text-sm shadow-lg",
          toast.isError ? "border-short bg-short/10 text-short" : "border-border bg-card text-foreground"
        )}>
          {toast.msg}
        </div>
      )}

      {confirmStop && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60">
          <Card className="w-80 border-short">
            <CardHeader className="!justify-start gap-2">
              <AlertTriangle className="h-4 w-4 text-short" />
              <span className="text-sm font-semibold">Confirm emergency stop</span>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-xs text-muted-foreground">
                Cancels all open orders and closes every non-grid position. Not yet wired to the
                real /api/dashboard/emergency-stop endpoint — this will only show a mock toast
                until that's connected.
              </p>
              <div className="flex gap-2">
                <Button variant="secondary" className="flex-1" onClick={() => setConfirmStop(false)}>Cancel</Button>
                <Button variant="destructive" className="flex-1" onClick={() => { setConfirmStop(false); notify("Emergency stop triggered (mock — not wired yet)") }}>
                  Stop everything
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}

function App() {
  const { status, checkAuth } = useAuth()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  if (status === "checking") {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background text-sm text-muted-foreground">
        Checking session…
      </div>
    )
  }

  if (status === "unauthenticated") {
    return <Login />
  }

  return <Dashboard />
}

export default App
