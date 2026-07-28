const blocks = [
  {
    top: "36%",
    left: "18%",
    width: "12%",
    height: "9%",
    label: "Bullish OB",
    color: "border-green-500/40 bg-green-500/10",
  },
  {
    top: "14%",
    left: "58%",
    width: "14%",
    height: "8%",
    label: "Bearish OB",
    color: "border-red-500/40 bg-red-500/10",
  },
];

export default function OrderBlockOverlay() {
  return (
    <>
      {blocks.map((block) => (
        <div
          key={block.label}
          className={`pointer-events-none absolute border ${block.color}`}
          style={{
            top: block.top,
            left: block.left,
            width: block.width,
            height: block.height,
          }}
        >
          <div className="absolute left-1 top-1 rounded bg-black/70 px-1 py-0.5 text-[9px] text-white/70">
            {block.label}
          </div>
        </div>
      ))}
    </>
  );
}
