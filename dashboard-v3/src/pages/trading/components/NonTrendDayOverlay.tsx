export default function NonTrendDayOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[30%] top-[34%] h-[22%] w-[40%] rounded border border-orange-400/50 bg-orange-500/10" />
      <div className="pointer-events-none absolute left-[38%] top-[30%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-orange-300">
        Non-Trend Day
      </div>
    </>
  );
}
