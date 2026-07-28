const phases = [
  {
    left: "18%",
    top: "63%",
    label: "Accumulation",
  },
  {
    left: "42%",
    top: "49%",
    label: "Manipulation",
  },
  {
    left: "69%",
    top: "23%",
    label: "Distribution",
  },
];

export default function PowerOfThreeOverlay() {
  return (
    <>
      {phases.map((phase) => (
        <div
          key={phase.label}
          className="pointer-events-none absolute rounded border border-violet-400/60 bg-violet-500/10 px-2 py-1"
          style={{
            left: phase.left,
            top: phase.top,
          }}
        >
          <span className="text-[9px] font-semibold text-violet-300">
            {phase.label}
          </span>
        </div>
      ))}
    </>
  );
}
