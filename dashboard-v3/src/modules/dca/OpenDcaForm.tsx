import { useCallback, useEffect, useRef, useState } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface OpenDcaFormProps {
  onResult: (msg: string, isError: boolean) => void
  onSuccess?: () => void
  triggerRefresh?: () => void
}

interface LadderLevel { level: number; price: number; size: number; notional: number; meets_exchange_min: boolean }
interface DcaPreview {
  can_execute: boolean; errors: string[]; warnings: string[]
  asset: string; side: string; exchange: string
  price: number | null; atr: number | null; balance: number | null
  risk_pct: number | null; risk_amount: number | null; sl_distance: number | null
  base_size: number | null; base_notional: number | null
  sl: number | null; tp1: number | null; tp2: number | null; tp3: number | null; trailing_stop: number | null
  max_levels: number | null; spacing_pct: number | null; size_multiplier: number | null
  ladder: LadderLevel[]; total_exposure: number | null; exchange_min_notional: number | null
}
interface DcaAssets { assets: string[]; open: string[] }

const usd = (v: number | null | undefined, dp = 2) =>
  v == null ? "—" : `$${v.toLocaleString(undefined, { minimumFractionDigits: dp, maximumFractionDigits: dp })}`
const num = (v: number | null | undefined, dp = 6) =>
  v == null ? "—" : v.toLocaleString(undefined, { minimumFractionDigits: dp, maximumFractionDigits: dp })

export function OpenDcaForm({ onResult, onSuccess, triggerRefresh }: OpenDcaFormProps) {
  const [assets, setAssets] = useState<string[]>([])
  const [openAssets, setOpenAssets] = useState<string[]>([])
  const [assetSearch, setAssetSearch] = useState("")
  const [asset, setAsset] = useState<string>("")
  const [side, setSide] = useState<"LONG" | "SHORT">("LONG")
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const [plan, setPlan] = useState<DcaPreview | null>(null)
  const [loadingPlan, setLoadingPlan] = useState(false)
  const [planError, setPlanError] = useState<string | null>(null)

  // Editable overrides (strings for controlled inputs; blank = use computed default)
  const [ovRisk, setOvRisk] = useState("")
  const [ovSl, setOvSl] = useState("")
  const [ovTp1, setOvTp1] = useState("")
  const [ovTp2, setOvTp2] = useState("")
  const [ovTp3, setOvTp3] = useState("")
  const [ovLevels, setOvLevels] = useState("")
  const [ovSpacing, setOvSpacing] = useState("")
  const [ovMult, setOvMult] = useState("")

  const reqSeq = useRef(0)

  // Bounded asset bar (config-driven; no hardcoded list)
  useEffect(() => {
    apiFetch<DcaAssets>("/dca/assets")
      .then((d) => {
        setAssets(d.assets)
        setOpenAssets(d.open)
        setAsset((cur) =>
          cur && d.assets.includes(cur)
            ? cur
            : d.assets[0] ?? ""
        )
      })
      .catch((e) => setPlanError(e instanceof ApiError ? e.message : "Failed to load assets"))
  }, [])

  // risk% is shown as a percent, backend wants a fraction
  const buildOverrides = useCallback(() => {
    const ov: Record<string, number> = {}
    if (ovRisk.trim() !== "") ov.risk_pct = parseFloat(ovRisk) / 100
    if (ovSl.trim() !== "") ov.sl = parseFloat(ovSl)
    if (ovTp1.trim() !== "") ov.tp1 = parseFloat(ovTp1)
    if (ovTp2.trim() !== "") ov.tp2 = parseFloat(ovTp2)
    if (ovTp3.trim() !== "") ov.tp3 = parseFloat(ovTp3)
    if (ovLevels.trim() !== "") ov.levels = parseInt(ovLevels)
    if (ovSpacing.trim() !== "") ov.spacing_pct = parseFloat(ovSpacing)
    if (ovMult.trim() !== "") ov.size_multiplier = parseFloat(ovMult)
    return ov
  }, [ovRisk, ovSl, ovTp1, ovTp2, ovTp3, ovLevels, ovSpacing, ovMult])

  // Debounced live re-preview on asset/side/override change (no per-keystroke API storm)
  useEffect(() => {
    const seq = ++reqSeq.current
    setLoadingPlan(true)
    setPlanError(null)
    const params = new URLSearchParams({ asset, side })
    for (const [k, v] of Object.entries(buildOverrides())) params.set(k, String(v))
    const t = setTimeout(() => {
      apiFetch<DcaPreview>(`/dca/preview?${params.toString()}`)
        .then((p) => { if (seq === reqSeq.current) setPlan(p) })
        .catch((e) => { if (seq === reqSeq.current) { setPlan(null); setPlanError(e instanceof ApiError ? e.message : "Failed to load preview") } })
        .finally(() => { if (seq === reqSeq.current) setLoadingPlan(false) })
    }, 400)
    return () => clearTimeout(t)
  }, [asset, side, buildOverrides])

  const canConfirm = !!plan?.can_execute && !loadingPlan && !planError

  const submit = async () => {
    if (!otp) { onResult("OTP code is required", true); return }
    if (!canConfirm) { onResult("This DCA cannot be opened — review the order ticket above.", true); return }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/dca/open", {
        method: "POST",
        body: JSON.stringify({
          asset,
          side,
          otp,
          exchange: plan?.exchange,
          overrides: buildOverrides(),
        }),
      })
      onResult(result.message || "DCA position opened", false)
      if (onSuccess) onSuccess()
      setOtp("")
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      onResult(e instanceof ApiError ? e.message : "Failed to open DCA position", true)
    } finally {
      setSubmitting(false)
    }
  }

  const editClass = "w-24 rounded-md border border-input bg-background px-2 py-1 font-mono text-xs outline-none text-right"
  const inputClass = "w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none"
  const rowClass = "flex items-center justify-between gap-2 py-0.5"
  const labelClass = "text-muted-foreground"
  const valClass = "font-mono text-right"

  const filteredAssets = assets.filter((a) => a.toLowerCase().includes(assetSearch.toLowerCase()))

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border bg-secondary/50 p-3 text-xs text-muted-foreground">
        Size, entry, SL/TP and the ladder are computed live from market data and your risk config, then
        validated against the {plan?.exchange ?? "exchange"} minimum. Adjust any field to run a what-if —
        the ticket re-prices automatically. Tradeable set is config-driven (default BTC/ETH).
      </div>

      {/* Bounded, searchable asset bar */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Asset</label>
        <input value={assetSearch} onChange={(e) => setAssetSearch(e.target.value)} placeholder="Search…" className={inputClass} />
        <div className="flex flex-wrap gap-2">
          {filteredAssets.map((a) => (
            <button key={a} onClick={() => setAsset(a)}
              className={cn("rounded-md px-3 py-1.5 text-sm font-semibold transition-colors",
                asset === a ? "bg-primary/15 text-primary" : "bg-secondary text-muted-foreground")}>
              {a}{openAssets.includes(a) ? " ●" : ""}
            </button>
          ))}
          {filteredAssets.length === 0 && <span className="text-xs text-muted-foreground">No tradeable assets match.</span>}
        </div>
        {openAssets.includes(asset) && (
          <div className="text-xs text-yellow-600 dark:text-yellow-400">● {asset} already has an open position — DCA will be blocked.</div>
        )}
      </div>

      {/* Direction */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Direction</label>
        <div className="flex gap-2">
          {(["LONG", "SHORT"] as const).map((s) => (
            <button key={s} onClick={() => setSide(s)}
              className={cn("flex-1 rounded-md py-2 text-sm font-semibold capitalize transition-colors",
                side === s ? (s === "LONG" ? "bg-long text-background" : "bg-short text-background") : "bg-secondary text-muted-foreground")}>
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Editable parameters */}
      <div className="space-y-2 rounded-md border border-border bg-background p-3">
        <label className="text-xs text-muted-foreground">Adjustable parameters (blank = computed default)</label>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <label className="flex items-center justify-between gap-1">Risk %<input value={ovRisk} onChange={(e) => setOvRisk(e.target.value)} placeholder={plan?.risk_pct != null ? (plan.risk_pct * 100).toFixed(2) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">Stop-loss<input value={ovSl} onChange={(e) => setOvSl(e.target.value)} placeholder={plan?.sl != null ? plan.sl.toFixed(2) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">TP1<input value={ovTp1} onChange={(e) => setOvTp1(e.target.value)} placeholder={plan?.tp1 != null ? plan.tp1.toFixed(2) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">TP2<input value={ovTp2} onChange={(e) => setOvTp2(e.target.value)} placeholder={plan?.tp2 != null ? plan.tp2.toFixed(2) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">TP3<input value={ovTp3} onChange={(e) => setOvTp3(e.target.value)} placeholder={plan?.tp3 != null ? plan.tp3.toFixed(2) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">Levels<input value={ovLevels} onChange={(e) => setOvLevels(e.target.value)} placeholder={plan?.max_levels != null ? String(plan.max_levels) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">Spacing %<input value={ovSpacing} onChange={(e) => setOvSpacing(e.target.value)} placeholder={plan?.spacing_pct != null ? String(plan.spacing_pct) : ""} className={editClass} /></label>
          <label className="flex items-center justify-between gap-1">Size ×<input value={ovMult} onChange={(e) => setOvMult(e.target.value)} placeholder={plan?.size_multiplier != null ? String(plan.size_multiplier) : ""} className={editClass} /></label>
        </div>
      </div>

      {/* Computed ticket (live, read-only derived) */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Computed order ticket (live)</label>
        {loadingPlan && <div className="text-xs text-muted-foreground">Re-pricing…</div>}
        {planError && <div className="rounded-md border border-destructive/50 bg-destructive/10 p-3 text-xs text-destructive">{planError}</div>}
        {plan && !loadingPlan && !planError && (
          <div className="space-y-2 rounded-md border border-border bg-background p-3 text-xs">
            {plan.errors.length > 0 && (
              <div className="rounded-md border border-destructive/50 bg-destructive/10 p-2 text-destructive">
                <div className="mb-1 font-semibold">Cannot open:</div>
                <ul className="list-disc space-y-0.5 pl-4">{plan.errors.map((e, i) => <li key={i}>{e}</li>)}</ul>
              </div>
            )}
            {plan.warnings.length > 0 && (
              <div className="rounded-md border border-yellow-500/50 bg-yellow-500/10 p-2 text-yellow-600 dark:text-yellow-400">
                <div className="mb-1 font-semibold">Warnings:</div>
                <ul className="list-disc space-y-0.5 pl-4">{plan.warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
              </div>
            )}
            <div className={rowClass}><span className={labelClass}>Entry (live)</span><span className={valClass}>{usd(plan.price)}</span></div>
            <div className={rowClass}><span className={labelClass}>ATR (1h)</span><span className={valClass}>{usd(plan.atr)}</span></div>
            <div className={rowClass}><span className={labelClass}>Balance</span><span className={valClass}>{usd(plan.balance)}</span></div>
            <div className={rowClass}><span className={labelClass}>Risk</span><span className={valClass}>{plan.risk_pct != null ? `${(plan.risk_pct * 100).toFixed(2)}% (${usd(plan.risk_amount)})` : "—"}</span></div>
            <div className={rowClass}><span className={labelClass}>Base size</span><span className={valClass}>{num(plan.base_size)} ({usd(plan.base_notional)})</span></div>
            <div className={rowClass}><span className={labelClass}>Stop-loss</span><span className={valClass}>{usd(plan.sl)}</span></div>
            <div className={rowClass}><span className={labelClass}>TP1 / TP2 / TP3</span><span className={valClass}>{usd(plan.tp1)} / {usd(plan.tp2)} / {usd(plan.tp3)}</span></div>
            <div className={rowClass}><span className={labelClass}>Trailing stop</span><span className={valClass}>{usd(plan.trailing_stop)}</span></div>
            <div className={rowClass}><span className={labelClass}>Ladder</span><span className={valClass}>{plan.max_levels ?? "—"} lv · {plan.spacing_pct ?? "—"}% · ×{plan.size_multiplier ?? "—"}</span></div>
            {plan.ladder.length > 0 && (
              <div className="mt-1 space-y-1 border-t border-border pt-2">
                {plan.ladder.map((l) => (
                  <div key={l.level} className={rowClass}>
                    <span className={labelClass}>L{l.level} @ {usd(l.price)}</span>
                    <span className={valClass}>{num(l.size)} · {usd(l.notional)} <span className={l.meets_exchange_min ? "text-green-500" : "text-destructive"}>{l.meets_exchange_min ? "✓ min" : "✗ <min"}</span></span>
                  </div>
                ))}
                <div className={rowClass}><span className={labelClass}>Total exposure</span><span className={valClass}>{usd(plan.total_exposure)}</span></div>
                <div className={rowClass}><span className={labelClass}>Exchange min</span><span className={valClass}>{usd(plan.exchange_min_notional)}</span></div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* OTP */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">OTP Code</label>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className={inputClass} />
      </div>
      <Button className="w-full" onClick={submit} disabled={submitting || !canConfirm}>
        {submitting ? "Opening DCA…" : !canConfirm ? "Cannot Open (see ticket)" : "Open DCA Position"}
      </Button>
    </div>
  )
}
