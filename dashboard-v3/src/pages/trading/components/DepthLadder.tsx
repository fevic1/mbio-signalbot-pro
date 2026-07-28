const bids = [
  ["118,460.5", "2.148"],
  ["118,460.0", "4.523"],
  ["118,459.5", "7.931"],
  ["118,459.0", "11.287"],
  ["118,458.5", "15.641"],
];

const asks = [
  ["118,462.5", "1.876"],
  ["118,463.0", "3.944"],
  ["118,463.5", "6.120"],
  ["118,464.0", "8.855"],
  ["118,464.5", "12.436"],
];

export default function DepthLadder() {
  return (
    <div className="absolute right-16 top-4 z-20 w-56 rounded-lg border border-white/10 bg-[#0b0f17]/95 backdrop-blur">
      <div className="border-b border-white/10 px-3 py-2 text-xs font-semibold text-white">
        Order Book
      </div>

      <div className="grid grid-cols-2 gap-4 p-3 text-[11px]">
        <div>
          <div className="mb-2 text-green-400">Bids</div>

          {bids.map(([price, size]) => (
            <div
              key={price}
              className="mb-1 flex justify-between text-green-400"
            >
              <span>{price}</span>
              <span className="text-white/70">{size}</span>
            </div>
          ))}
        </div>

        <div>
          <div className="mb-2 text-red-400">Asks</div>

          {asks.map(([price, size]) => (
            <div
              key={price}
              className="mb-1 flex justify-between text-red-400"
            >
              <span>{price}</span>
              <span className="text-white/70">{size}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
