const bands = [
  {
    top: "39%",
    label: "+2σ",
  },
  {
    top: "43%",
    label: "+1σ",
  },
  {
    top: "51%",
    label: "-1σ",
  },
  {
    top: "56%",
    label: "-2σ",
  },
];

export default function VWAPBandsOverlay() {
  return (
    <>
      {bands.map((band) => (
        <div
          key={band.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-cyan-300/25"
          style={{ top: band.top }}
        >
          <span className="absolute right-2 -top-4 text-[9px] text-cyan-300/80">
            {band.label}
          </span>
        </div>
      ))}
    </>
  );
}
