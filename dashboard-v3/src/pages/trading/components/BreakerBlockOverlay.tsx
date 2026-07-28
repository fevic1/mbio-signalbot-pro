const breakers = [
  {
    top: "41%",
    left: "37%",
    width: "11%",
    height: "7%",
    label: "Breaker",
  },
  {
    top: "66%",
    left: "56%",
    width: "10%",
    height: "6%",
    label: "Breaker",
  },
];

export default function BreakerBlockOverlay() {
  return (
    <>
      {breakers.map((item, index) => (
        <div
          key={index}
          className="pointer-events-none absolute border border-violet-400/50 bg-violet-500/10"
          style={{
            top: item.top,
            left: item.left,
            width: item.width,
            height: item.height,
          }}
        >
          <span className="absolute left-1 top-1 text-[9px] text-violet-300">
            {item.label}
          </span>
        </div>
      ))}
    </>
  );
}
