const blocks = [
  {
    top: "22%",
    left: "73%",
    width: "10%",
    height: "6%",
  },
  {
    top: "57%",
    left: "15%",
    width: "12%",
    height: "7%",
  },
];

export default function MitigationBlockOverlay() {
  return (
    <>
      {blocks.map((block, index) => (
        <div
          key={index}
          className="pointer-events-none absolute border border-emerald-400/50 bg-emerald-500/10"
          style={{
            top: block.top,
            left: block.left,
            width: block.width,
            height: block.height,
          }}
        >
          <span className="absolute left-1 top-1 text-[9px] text-emerald-300">
            Mitigation
          </span>
        </div>
      ))}
    </>
  );
}
