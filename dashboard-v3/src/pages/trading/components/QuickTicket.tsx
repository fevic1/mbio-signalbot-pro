import { ArrowLeft } from "lucide-react";

interface Props {
  onBack: () => void;
}

export default function QuickTicket({ onBack }: Props) {
  return (
    <div className="p-5 space-y-5">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300"
      >
        <ArrowLeft className="h-4 w-4" />
        Back
      </button>

      <div>
        <h2 className="text-lg font-semibold text-white">
          Quick Ticket
        </h2>

        <p className="text-sm text-white/50">
          Manual order execution.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-xs text-white/60">
            Symbol
          </label>

          <select className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white">
            <option>BTC</option>
            <option>ETH</option>
            <option>SOL</option>
          </select>
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/60">
            Side
          </label>

          <div className="grid grid-cols-2 gap-2">
            <button className="rounded-lg bg-green-600 py-2 font-medium text-white">
              BUY
            </button>

            <button className="rounded-lg bg-red-600 py-2 font-medium text-white">
              SELL
            </button>
          </div>
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/60">
            Size
          </label>

          <input
            type="number"
            placeholder="0.00"
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white outline-none"
          />
        </div>

        <div>
          <label className="mb-2 block text-xs text-white/60">
            Price
          </label>

          <input
            type="number"
            placeholder="Market"
            className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-white outline-none"
          />
        </div>

        <button className="w-full rounded-lg bg-cyan-500 py-3 font-semibold text-black transition hover:bg-cyan-400">
          Submit Order
        </button>
      </div>
    </div>
  );
}
