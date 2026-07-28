const phases = [
  {
    title: "Accumulation",
    top: "16%",
    left: "10%",
    width: "18%",
    height: "12%",
  },
  {
    title: "Expansion",
    top: "34%",
    left: "36%",
    width: "26%",
    height: "18%",
  },
  {
    title: "Distribution",
    top: "63%",
    left: "60%",
    width: "18%",
    height: "12%",
  },
];

export default function AuctionPhaseOverlay() {
  return (
    <>
      {phases.map((phase) => (
        <div
          key={phase.title}
          className="pointer-events-none absolute rounded border border-indigo-400/50 bg-indigo-500/10"
          style={{
            top: phase.top,
            left: phase.left,
            width: phase.width,
            height: phase.height,
          }}
        >
          <div className="absolute left-2 top-2 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-indigo-300">
            {phase.title}
          </div>
        </div>
      ))}
    </>
  );
}
