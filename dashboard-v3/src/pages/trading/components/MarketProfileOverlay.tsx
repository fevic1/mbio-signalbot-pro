const profiles = [
  {
    top: "18%",
    height: "24%",
    side: "left",
  },
  {
    top: "51%",
    height: "29%",
    side: "right",
  },
];

export default function MarketProfileOverlay() {
  return (
    <>
      {profiles.map((profile, index) => (
        <div
          key={index}
          className={`pointer-events-none absolute ${profile.side === "left" ? "left-12" : "right-16"} w-10 rounded bg-yellow-400/10 border border-yellow-400/40`}
          style={{
            top: profile.top,
            height: profile.height,
          }}
        >
          <div className="flex h-full items-center justify-center text-[9px] text-yellow-300 rotate-90">
            TPO
          </div>
        </div>
      ))}
    </>
  );
}
