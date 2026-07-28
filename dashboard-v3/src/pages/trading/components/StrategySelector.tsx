import {
  Zap,
  Grid2X2,
  Layers3,
} from "lucide-react";

interface Props {
  onQuickTicket: () => void;
  onGrid: () => void;
  onDCA: () => void;
}

function StrategyCard({
  icon,
  title,
  description,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full rounded-lg border border-white/10 bg-white/5 p-4 text-left transition hover:border-cyan-400 hover:bg-white/10"
    >
      <div className="mb-3 text-cyan-400">{icon}</div>

      <div className="font-semibold text-white">
        {title}
      </div>

      <div className="mt-1 text-sm text-white/50">
        {description}
      </div>
    </button>
  );
}

export default function StrategySelector({
  onQuickTicket,
  onGrid,
  onDCA,
}: Props) {
  return (
    <div className="space-y-4 p-5">
      <div>
        <h2 className="text-lg font-semibold text-white">
          Create Strategy
        </h2>

        <p className="text-sm text-white/50">
          Select a trading strategy to configure.
        </p>
      </div>

      <StrategyCard
        icon={<Zap className="h-6 w-6" />}
        title="Quick Ticket"
        description="Single manual trade execution."
        onClick={onQuickTicket}
      />

      <StrategyCard
        icon={<Grid2X2 className="h-6 w-6" />}
        title="Grid Bot"
        description="Market-neutral grid strategy."
        onClick={onGrid}
      />

      <StrategyCard
        icon={<Layers3 className="h-6 w-6" />}
        title="DCA Bot"
        description="Dollar-cost averaging strategy."
        onClick={onDCA}
      />
    </div>
  );
}
