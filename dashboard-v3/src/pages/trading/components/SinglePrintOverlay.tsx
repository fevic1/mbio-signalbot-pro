const prints = [
  {
    top: "38%",
    height: "5%",
  },
  {
    top: "73%",
    height: "4%",
  },
];

export default function SinglePrintOverlay() {
  return (
    <>
      {prints.map((print, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16 border border-fuchsia-400/50 bg-fuchsia-500/10"
          style={{
            top: print.top,
            height: print.height,
          }}
        >
          <div className="absolute right-2 top-1 text-[9px] text-fuchsia-300">
            Single Print
          </div>
        </div>
      ))}
    </>
  );
}
