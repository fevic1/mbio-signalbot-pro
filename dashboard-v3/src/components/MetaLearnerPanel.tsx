import { useEffect, useState } from "react"
import { apiFetch } from "@/lib/api"
import { Card, CardHeader, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface MetaLearnerData {
  weights: Record<string, Record<string, number>>
  strategies: string[]
  regimes: string[]
}

export function MetaLearnerPanel() {
  const [data, setData] = useState<MetaLearnerData | null>(null)
  const [selectedRegime, setSelectedRegime] = useState<string>("RANGING")

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await apiFetch<MetaLearnerData>("/meta_learner")
        setData(res)
        if (res.regimes && res.regimes.length > 0 && !res.regimes.includes(selectedRegime)) {
          setSelectedRegime(res.regimes[0])
        }
      } catch (e) {
        console.error("Failed to load meta learner", e)
      }
    }
    fetch()
    const id = setInterval(fetch, 30000) // Refresh every 30s
    return () => clearInterval(id)
  }, [selectedRegime])

  if (!data) return <p className="text-sm text-muted-foreground">Loading AI Strategy Weights...</p>

  const currentWeights = data.weights[selectedRegime] || {}

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-semibold">🧠 AI Ensemble & Meta-Learner</span>
            <Badge variant="default" className="text-xs">6 Strategies</Badge>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 mt-2">
          {data.regimes.map((regime) => (
            <button
              key={regime}
              onClick={() => setSelectedRegime(regime)}
              className={`px-2 py-1 text-xs rounded-md transition-colors ${
                selectedRegime === regime 
                  ? "bg-primary text-primary-foreground" 
                  : "bg-secondary text-muted-foreground hover:bg-secondary/80"
              }`}
            >
              {regime.replace("_", " ")}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.strategies.map((strat) => {
            const weight = currentWeights[strat] || 0
            const percentage = Math.round(weight * 100)
            return (
              <div key={strat} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-muted-foreground">{strat}</span>
                  <span className="font-mono font-semibold">{percentage}%</span>
                </div>
                <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-primary transition-all duration-500" 
                    style={{ width: `${percentage}%` }} 
                  />
                </div>
              </div>
            )
          })}
        </div>
        <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
          <p>The Meta-Learner dynamically adjusts strategy weights based on trade outcomes (PnL) in each market regime using Bayesian updating. The Ensemble Vote requires a 4/6 majority (70%+ confidence) to execute.</p>
        </div>
      </CardContent>
    </Card>
  )
}
