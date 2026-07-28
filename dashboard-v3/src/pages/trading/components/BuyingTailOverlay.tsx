const tails = [
  {
    left: "16%",
    top: "82%",
    height: "12%",
  },
];

export default function BuyingTailOverlay() {
  return (
    <>
      {tails.map((tail, index) => (
        <div
          key={index}
          className="pointer-events-none absolute w-1 rounded bg-emerald-400/80"
          style={{
            left: tail.left,
            top: tail.top,
            height: tail.height,
          }}
        />
      ))}

      <div className="pointer-events-none absolute left-[17%] top-[79%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-emerald-300">
        Buying Tail
      </div>
    </>
  );
}
