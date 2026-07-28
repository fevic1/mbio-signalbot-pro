import { useState } from "react";
import { ArrowLeft, Grid3x3, TrendingUp } from "lucide-react";

type Strategy = "GRID" | "DCA" | null;

interface StrategySelectorProps {
  onBack: () => void;
  onSelectStrategy: (strategy: "GRID" | "DCA") => void;
}

export default function StrategySelector({
  onBack,
  onSelectStrategy,
}: StrategySelectorProps) {
  const [selected, setSelected] = useState<Strategy>(null);

  if (selected === null) {
    return (
      <div className="flex h-full flex-col overflow-hidden bg-gray-950">

        <div className="flex items-center border-b border-white/10 px-4 py-3">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-sm text-white/60 transition hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">

          <h2 className="mb-5 text-sm font-semibold text-white">
            Select Strategy
          </h2>

          <div className="space-y-3">

            <button
              onClick={() => {
  setSelected("GRID");
  onSelectStrategy("GRID");
}}
              className="flex w-full items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-5 text-left transition hover:border-cyan-400 hover:bg-white/10"
            >
              <div className="rounded-lg bg-cyan-500/10 p-3 text-cyan-400">
                <Grid3x3 className="h-6 w-6" />
              </div>

              <div>
                <div className="font-semibold text-white">
                  GRID Bot
                </div>

                <p className="mt-1 text-xs text-white/50">
                  Market-neutral range trading strategy.
                </p>
              </div>
            </button>

            <button
              onClick={() => {
  setSelected("DCA");
  onSelectStrategy("DCA");
}}
              className="flex w-full items-start gap-4 rounded-xl border border-white/10 bg-white/5 p-5 text-left transition hover:border-cyan-400 hover:bg-white/10"
            >
              <div className="rounded-lg bg-cyan-500/10 p-3 text-cyan-400">
                <TrendingUp className="h-6 w-6" />
              </div>

              <div>
                <div className="font-semibold text-white">
                  DCA Bot
                </div>

                <p className="mt-1 text-xs text-white/50">
                  Dollar-cost averaging trend strategy.
                </p>
              </div>
            </button>

          </div>

        </div>

      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden bg-gray-950">

      <div className="flex items-center border-b border-white/10 px-4 py-3">
        <button
          onClick={() => setSelected(null)}
          className="flex items-center gap-2 text-sm text-white/60 transition hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4">

        <div className="rounded-xl border border-white/10 bg-white/5 p-5">

          <h3 className="mb-2 text-base font-semibold text-white">
            {selected} Configuration
          </h3>

          <p className="mb-6 text-sm text-white/50">
            Builder UI for {selected} will be inserted here.
          </p>

          <div className="rounded-lg border border-dashed border-white/10 p-10 text-center text-white/30">
            {selected} Builder Placeholder
          </div>

        </div>

      </div>

    </div>
  );
}
