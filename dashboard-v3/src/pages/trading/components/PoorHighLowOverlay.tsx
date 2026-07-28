const levels = [
  {
    top: "12%",
    label: "Poor High",
  },
  {
    top: "82%",
    label: "Poor Low",
  },
];

export default function PoorHighLowOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: level.top }}
        >
          <div className="border-t-2 border-red-400" />
          <div className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
            {level.label}
          </div>
        </div>
      ))}
    </>
  );
}
