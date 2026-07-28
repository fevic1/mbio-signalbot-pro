const markers = [
  {
    top: "56%",
    label: "Entry 118,462",
    color: "bg-cyan-500",
  },
  {
    top: "42%",
    label: "Take Profit",
    color: "bg-green-500",
  },
  {
    top: "68%",
    label: "Stop Loss",
    color: "bg-red-500",
  },
];

export default function PositionMarkers() {
  return (
    <>
      {markers.map((marker) => (
        <div
          key={marker.label}
          className="pointer-events-none absolute left-12 right-16 z-20"
          style={{ top: marker.top }}
        >
          <div className={`h-[2px] w-full ${marker.color}`} />

          <div className="absolute right-2 -top-3 rounded bg-[#0b0f17]/95 px-2 py-1 text-[10px] text-white">
            {marker.label}
          </div>
        </div>
      ))}
    </>
  );
}
