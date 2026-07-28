const pairs = [
  {
    top: "34%",
    left: "33%",
    width: "18%",
  },
  {
    top: "66%",
    left: "57%",
    width: "15%",
  },
];

export default function SMTDivergenceOverlay() {
  return (
    <>
      {pairs.map((pair, index) => (
        <div
          key={index}
          className="pointer-events-none absolute"
          style={{
            top: pair.top,
            left: pair.left,
            width: pair.width,
          }}
        >
          <div className="border-t-2 border-dotted border-fuchsia-400" />
          <div className="mt-1 text-[9px] text-fuchsia-300">
            SMT Divergence
          </div>
        </div>
      ))}
    </>
  );
}
