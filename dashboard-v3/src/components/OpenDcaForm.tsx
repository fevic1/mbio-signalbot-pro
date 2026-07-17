import { useState } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface OpenDcaFormProps {
  onResult: (msg: string, isError: boolean) => void
  onSuccess?: () => void
  triggerRefresh?: () => void
}

export function OpenDcaForm({ onResult, onSuccess, triggerRefresh }: OpenDcaFormProps) {
  const [asset, setAsset] = useState<"BTC" | "ETH">("BTC")
  const [side, setSide] = useState<"LONG" | "SHORT">("LONG")
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!otp) {
      onResult("OTP code is required", true)
      return
    }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/dca/open", {
        method: "POST",
        body: JSON.stringify({ asset, side, otp }),
      })
      onResult(result.message || "DCA position opened", false)
      if (onSuccess) onSuccess() // Triggers auto-close ("slide away")
      setOtp("")
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Failed to open DCA position"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  const inputClass = "w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none"

  return (
    <div className="space-y-4">
      <div className="rounded-md border border-border bg-secondary/50 p-3 text-xs text-muted-foreground">
        Size, entry, and stop-loss are computed automatically from live market data and account
        risk config (1% of balance) — not user-set here. BTC and ETH only.
      </div>
      
      {/* Asset Toggle */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Asset</label>
        <div className="flex gap-2">
          {(["BTC", "ETH"] as const).map((a) => (
            <button
              key={a}
              onClick={() => setAsset(a)}
              className={cn(
                "flex-1 rounded-md py-2 text-sm font-semibold transition-colors",
                asset === a ? "bg-primary/15 text-primary" : "bg-secondary text-muted-foreground"
              )}
            >
              {a}
            </button>
          ))}
        </div>
      </div>

      {/* Direction Toggle */}
      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">Direction</label>
        <div className="flex gap-2">
          {(["LONG", "SHORT"] as const).map((s) => (
            <button
              key={s}
              onClick={() => setSide(s)}
              className={cn(
                "flex-1 rounded-md py-2 text-sm font-semibold capitalize transition-colors",
                side === s ? (s === "LONG" ? "bg-long text-background" : "bg-short text-background") : "bg-secondary text-muted-foreground"
              )}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-xs text-muted-foreground">OTP Code</label>
        <input value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className={inputClass} />
      </div>
      <Button className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Opening DCA…" : "Open DCA Position"}
      </Button>
    </div>
  )
}
