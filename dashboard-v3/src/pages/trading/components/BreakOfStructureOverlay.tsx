const breaks = [
  {
    left: "34%",
    top: "42%",
    width: "17%",
    label: "BOS",
  },
  {
    left: "64%",
    top: "70%",
    width: "16%",
    label: "CHOCH",
  },
];

export default function BreakOfStructureOverlay() {
  return (
    <>
      {breaks.map((item) => (
        <div
          key={item.label}
          className="pointer-events-none absolute"
          style={{
            left: item.left,
            top: item.top,
            width: item.width,
          }}
        >
          <div className="border-t-2 border-amber-400" />
          <div className="mt-1 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-amber-300 inline-block">
            {item.label}
          </div>
        </div>
      ))}
    </>
  );
}
