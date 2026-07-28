import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiFetch } from '@/lib/api';
import { Brain, Shield, Zap, Activity, AlertCircle } from 'lucide-react';

interface MetaLearnerData {
  status: string;
  weights: Record<string, Record<string, number>>;
  strategies: string[];
  regimes: string[];
}

export function AIDecisionCenter() {
  const [data, setData] = useState<MetaLearnerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await apiFetch<MetaLearnerData>('/meta_learner');
        setData(res);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load AI status");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 30000); // 30s polling
    return () => clearInterval(interval);
  }, []);

  if (loading && !data) {
    return <Card><CardContent className="p-6 text-sm text-muted-foreground">Loading AI Decision Center...</CardContent></Card>;
  }

  if (error || !data || data.status === 'error') {
    return (
      <Card className="border-destructive/50">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 text-sm text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span>{error || 'AI Engine Offline'}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const activeRegime = data.regimes[0] || "RANGING";
  const activeWeights = data.weights[activeRegime] || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Brain className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">AI Decision Center</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Ensemble Weights */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              Ensemble Weights ({activeRegime})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(activeWeights).map(([strategy, weight]) => (
                <div key={strategy} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{strategy}</span>
                    <span className="text-muted-foreground">{(weight * 100).toFixed(1)}%</span>
                  </div>
                  <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary transition-all duration-500"
                      style={{ width: `${Math.max(5, weight * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
              {Object.keys(activeWeights).length === 0 && (
                <div className="text-sm text-muted-foreground">No weight data available for this regime.</div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* System Logic & Guards */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Shield className="h-4 w-4 text-muted-foreground" />
              Execution Guards
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2">
                <Zap className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />
                <div>
                  <span className="font-semibold">Sniper Override:</span>
                  <span className="text-muted-foreground ml-1">High-confidence signals bypass ensemble voting.</span>
                </div>
              </li>
              <li className="flex items-start gap-2">
                <Shield className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
                <div>
                  <span className="font-semibold">Regime Gate:</span>
                  <span className="text-muted-foreground ml-1">Blocks counter-trend trades (e.g., no SELL in TRENDING_UP).</span>
                </div>
              </li>
              <li className="flex items-start gap-2">
                <Activity className="h-4 w-4 text-blue-400 mt-0.5 shrink-0" />
                <div>
                  <span className="font-semibold">Dynamic Weighting:</span>
                  <span className="text-muted-foreground ml-1">Strategy weights adapt automatically to {data.regimes.join(', ')} regimes.</span>
                </div>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
