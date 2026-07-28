const levels = [
  { top: "43%", label: "Composite POC" },
  { top: "58%", label: "Developing POC" },
];

export default function CompositePOCOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: level.top }}
        >
          <div className="border-t-2 border-orange-400" />
          <div className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-orange-300">
            {level.label}
          </div>
        </div>
      ))}
    </>
  );
}
