export default function OpeningRangeBreakoutOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[33%] top-[20%] h-[18%] w-[34%] rounded border border-green-400 border-dashed bg-green-500/10" />
      <div className="pointer-events-none absolute left-[49%] top-[20%] h-[52%] border-l-2 border-green-400" />
      <div className="pointer-events-none absolute left-[35%] top-[16%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-green-300">
        Opening Range Breakout
      </div>
    </>
  );
}
