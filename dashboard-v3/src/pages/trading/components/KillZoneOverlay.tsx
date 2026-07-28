const zones = [
  {
    left: "14%",
    width: "12%",
    label: "London Kill Zone",
    color: "bg-cyan-500/8 border-cyan-400/25",
  },
  {
    left: "62%",
    width: "14%",
    label: "NY Kill Zone",
    color: "bg-purple-500/8 border-purple-400/25",
  },
];

export default function KillZoneOverlay() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className={`pointer-events-none absolute top-8 bottom-8 border ${zone.color}`}
          style={{
            left: zone.left,
            width: zone.width,
          }}
        >
          <div className="absolute left-1 top-1 rounded bg-black/70 px-2 py-0.5 text-[9px] text-white/60">
            {zone.label}
          </div>
        </div>
      ))}
    </>
  );
}
