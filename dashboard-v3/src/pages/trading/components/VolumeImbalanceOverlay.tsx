const zones = [
  {
    top: "24%",
    left: "27%",
    width: "7%",
    height: "18%",
  },
  {
    top: "49%",
    left: "61%",
    width: "6%",
    height: "14%",
  },
];

export default function VolumeImbalanceOverlay() {
  return (
    <>
      {zones.map((zone, index) => (
        <div
          key={index}
          className="pointer-events-none absolute rounded border border-red-300/50 bg-red-400/10"
          style={{
            top: zone.top,
            left: zone.left,
            width: zone.width,
            height: zone.height,
          }}
        >
          <div className="absolute inset-0 bg-[repeating-linear-gradient(-45deg,transparent,transparent_4px,rgba(255,255,255,0.08)_4px,rgba(255,255,255,0.08)_8px)]" />
        </div>
      ))}
    </>
  );
}
