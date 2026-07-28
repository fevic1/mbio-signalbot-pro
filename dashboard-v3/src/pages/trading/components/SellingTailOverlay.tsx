const tails = [
  {
    left: "74%",
    top: "6%",
    height: "12%",
  },
];

export default function SellingTailOverlay() {
  return (
    <>
      {tails.map((tail, index) => (
        <div
          key={index}
          className="pointer-events-none absolute w-1 rounded bg-red-400/80"
          style={{
            left: tail.left,
            top: tail.top,
            height: tail.height,
          }}
        />
      ))}

      <div className="pointer-events-none absolute left-[66%] top-[18%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Selling Tail
      </div>
    </>
  );
}
