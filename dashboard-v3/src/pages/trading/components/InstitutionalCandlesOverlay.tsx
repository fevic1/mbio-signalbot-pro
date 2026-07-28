const candles = [
  {
    top: "29%",
    left: "24%",
    label: "IB",
  },
  {
    top: "53%",
    left: "48%",
    label: "IFVG",
  },
  {
    top: "71%",
    left: "67%",
    label: "SMT",
  },
];

export default function InstitutionalCandlesOverlay() {
  return (
    <>
      {candles.map((item) => (
        <div
          key={item.label}
          className="pointer-events-none absolute rounded border border-cyan-400/60 bg-cyan-500/10 px-2 py-1"
          style={{
            top: item.top,
            left: item.left,
          }}
        >
          <span className="text-[9px] font-semibold text-cyan-300">
            {item.label}
          </span>
        </div>
      ))}
    </>
  );
}
