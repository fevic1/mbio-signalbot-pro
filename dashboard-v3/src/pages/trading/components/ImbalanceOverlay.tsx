const imbalances = [
  {
    top: "27%",
    left: "30%",
    width: "8%",
    height: "11%",
  },
  {
    top: "49%",
    left: "67%",
    width: "7%",
    height: "10%",
  },
];

export default function ImbalanceOverlay() {
  return (
    <>
      {imbalances.map((zone, index) => (
        <div
          key={index}
          className="pointer-events-none absolute border border-cyan-400/50 bg-cyan-400/10"
          style={{
            top: zone.top,
            left: zone.left,
            width: zone.width,
            height: zone.height,
          }}
        >
          <div className="absolute left-1 top-1 text-[9px] text-cyan-300">
            IMB
          </div>
        </div>
      ))}
    </>
  );
}
