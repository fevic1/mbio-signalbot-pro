const zones = [
  {
    top: "19%",
    label: "EQH",
    color: "border-red-400",
  },
  {
    top: "82%",
    label: "EQL",
    color: "border-green-400",
  },
];

export default function EqualHighsLowsOverlay() {
  return (
    <>
      {zones.map((zone) => (
        <div
          key={zone.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: zone.top }}
        >
          <div className={`border-t-2 border-dashed ${zone.color}`} />
          <span className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-white">
            {zone.label}
          </span>
        </div>
      ))}
    </>
  );
}
