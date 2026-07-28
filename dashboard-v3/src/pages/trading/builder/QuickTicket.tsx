
interface QuickTicketProps {
  onCreateBot: () => void;
}

export default function QuickTicket({
  onCreateBot,
}: QuickTicketProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-gray-950">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
        <div>
          <h2 className="text-sm font-semibold text-white">
            Quick Ticket
          </h2>
          <p className="mt-1 text-xs text-white/50">
            Manual execution
          </p>
        </div>

        <button
          onClick={onCreateBot}
          className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-1.5 text-xs font-medium text-cyan-400 transition hover:bg-cyan-500/20"
        >
          Create Bot
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">

        <div>
          <label className="mb-2 block text-xs text-white/50">
            Symbol
          </label>

          <select className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-cyan-400 focus:outline-none">
            <option>BTCUSDT</option>
            <option>ETHUSDT</option>
            <option>SOLUSDT</option>
          </select>
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/50">
            Order Type
          </label>

          <div className="grid grid-cols-2 gap-2">
            <button className="rounded-lg bg-cyan-500/20 py-2 text-sm font-medium text-cyan-400">
              Market
            </button>

            <button className="rounded-lg border border-white/10 bg-white/5 py-2 text-sm text-white/60">
              Limit
            </button>
          </div>
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/50">
            Quantity
          </label>

          <input
            type="number"
            placeholder="0.00"
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-white/30 focus:border-cyan-400 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/50">
            Leverage
          </label>

          <input
            type="number"
            defaultValue={5}
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white focus:border-cyan-400 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          <button className="rounded-lg bg-green-500/20 py-3 font-semibold text-green-400 transition hover:bg-green-500/30">
            Buy / Long
          </button>

          <button className="rounded-lg bg-red-500/20 py-3 font-semibold text-red-400 transition hover:bg-red-500/30">
            Sell / Short
          </button>
        </div>

      </div>

    </div>
  );
}
