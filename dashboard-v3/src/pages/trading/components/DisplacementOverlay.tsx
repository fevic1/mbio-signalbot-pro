const moves = [
  {
    left: "31%",
    top: "63%",
    width: "18%",
    rotation: "-24deg",
    color: "border-green-400",
    label: "Bullish Displacement",
  },
  {
    left: "59%",
    top: "24%",
    width: "16%",
    rotation: "28deg",
    color: "border-red-400",
    label: "Bearish Displacement",
  },
];

export default function DisplacementOverlay() {
  return (
    <>
      {moves.map((move) => (
        <div
          key={move.label}
          className="pointer-events-none absolute"
          style={{
            left: move.left,
            top: move.top,
            transform: `rotate(${move.rotation})`,
            width: move.width,
          }}
        >
          <div className={`border-t-2 ${move.color}`} />
          <span className="mt-1 block text-[9px] text-white/70">
            {move.label}
          </span>
        </div>
      ))}
    </>
  );
}
