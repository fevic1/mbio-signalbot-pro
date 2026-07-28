const levels = [
  { top: "36%" },
  { top: "38%" },
  { top: "40%" },
  { top: "42%" },
  { top: "44%" },
];

export default function DevelopingPOCOverlay() {
  return (
    <>
      {levels.map((level, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-16 right-20"
          style={{ top: level.top }}
        >
          <div className="border-t border-dashed border-yellow-300" />
        </div>
      ))}

      <div className="pointer-events-none absolute left-20 top-[35%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-yellow-300">
        Developing POC Trail
      </div>
    </>
  );
}
