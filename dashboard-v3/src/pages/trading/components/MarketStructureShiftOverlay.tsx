const shifts = [
  {
    left: "22%",
    top: "61%",
    width: "20%",
    label: "MSS ↑",
    color: "text-green-400",
  },
  {
    left: "57%",
    top: "28%",
    width: "18%",
    label: "MSS ↓",
    color: "text-red-400",
  },
];

export default function MarketStructureShiftOverlay() {
  return (
    <>
      {shifts.map((shift) => (
        <div
          key={shift.label}
          className="pointer-events-none absolute"
          style={{
            left: shift.left,
            top: shift.top,
            width: shift.width,
          }}
        >
          <div className="border-t border-yellow-300 border-dashed" />
          <div className={`mt-1 text-[9px] font-semibold ${shift.color}`}>
            {shift.label}
          </div>
        </div>
      ))}
    </>
  );
}
