type Trade = {
  time: string;
  price: string;
  size: string;
  side: "buy" | "sell";
};

const trades: Trade[] = [
  { time: "08:15:21", price: "118,462.3", size: "0.428", side: "buy" },
  { time: "08:15:20", price: "118,461.8", size: "1.104", side: "sell" },
  { time: "08:15:19", price: "118,462.0", size: "0.681", side: "buy" },
  { time: "08:15:18", price: "118,461.5", size: "2.240", side: "sell" },
  { time: "08:15:17", price: "118,460.9", size: "0.917", side: "buy" },
  { time: "08:15:16", price: "118,460.7", size: "3.582", side: "buy" },
  { time: "08:15:15", price: "118,460.3", size: "1.223", side: "sell" },
];

export default function OrderFlowTape() {
  return (
    <div className="absolute left-16 top-12 z-20 w-72 overflow-hidden rounded-xl border border-white/10 bg-[#09111b]/95 shadow-2xl backdrop-blur">
      <div className="flex items-center justify-between border-b border-white/10 px-4 py-2">
        <span className="text-xs font-semibold text-white">
          Time & Sales
        </span>

        <span className="text-[10px] uppercase tracking-widest text-cyan-400">
          Live
        </span>
      </div>

      <div className="max-h-64 overflow-y-auto">
        {trades.map((trade, index) => (
          <div
            key={index}
            className="grid grid-cols-3 border-b border-white/5 px-4 py-2 text-[11px]"
          >
            <span className="text-white/40">
              {trade.time}
            </span>

            <span
              className={
                trade.side === "buy"
                  ? "text-green-400"
                  : "text-red-400"
              }
            >
              {trade.price}
            </span>

            <span className="text-right text-white/70">
              {trade.size}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
