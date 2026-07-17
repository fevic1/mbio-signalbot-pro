import { useState } from "react"
import { apiFetch, ApiError } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface OpenGridFormProps {
  onResult: (msg: string, isError: boolean) => void
  onSuccess?: () => void
  triggerRefresh?: () => void
}

export function OpenGridForm({ onResult, onSuccess, triggerRefresh }: OpenGridFormProps) {
  const [asset, setAsset] = useState<"BTC" | "ETH">("BTC")
  const [lower, setLower] = useState("")
  const [upper, setUpper] = useState("")
  const [investment, setInvestment] = useState("")
  const [nodes, setNodes] = useState("10")
  const [otp, setOtp] = useState("")
  const [submitting, setSubmitting] = useState(false)

  const submit = async () => {
    if (!otp) {
      onResult("OTP code is required", true)
      return
    }
    if (!lower || !upper || !investment || !nodes) {
      onResult("All fields are required", true)
      return
    }
    setSubmitting(true)
    try {
      const result = await apiFetch<{ status: string; message: string }>("/grid/open", {
        method: "POST",
        body: JSON.stringify({
          asset,
          lower_price: parseFloat(lower),
          upper_price: parseFloat(upper),
          investment_amount: parseFloat(investment),
          num_nodes: parseInt(nodes),
          otp
        }),
      })
      onResult(result.message || "Grid opened successfully", false)
      if (onSuccess) onSuccess() // Triggers auto-close ("slide away")
      if (triggerRefresh) setTimeout(() => triggerRefresh(), 1000)
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Failed to open grid"
      onResult(msg, true)
    } finally {
      setSubmitting(false)
    }
  }

  const inputClass = "w-full rounded-md border border-input bg-background px-3 py-2 font-mono text-sm outline-none"

  return (
    <div className="space-y-4">
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

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="text-xs text-muted-foreground">Nodes</label>
          <input type="number" value={nodes} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNodes(e.target.value)} placeholder="10" className={inputClass} />
        </div>
        <div className="space-y-2">
          <label className="text-xs text-muted-foreground">Lower Price</label>
          <input type="number" value={lower} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLower(e.target.value)} placeholder="50000" className={inputClass} />
        </div>
        <div className="space-y-2">
          <label className="text-xs text-muted-foreground">Upper Price</label>
          <input type="number" value={upper} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUpper(e.target.value)} placeholder="70000" className={inputClass} />
        </div>
        <div className="space-y-2 col-span-2">
          <label className="text-xs text-muted-foreground">Investment (USD)</label>
          <input type="number" value={investment} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInvestment(e.target.value)} placeholder="100" className={inputClass} />
        </div>
        <div className="space-y-2 col-span-2">
          <label className="text-xs text-muted-foreground">OTP Code</label>
          <input value={otp} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOtp(e.target.value)} placeholder="6-digit code" maxLength={6} className={inputClass} />
        </div>
      </div>
      <Button className="w-full" onClick={submit} disabled={submitting}>
        {submitting ? "Opening Grid…" : "Open Grid"}
      </Button>
    </div>
  )
}
