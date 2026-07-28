export default function NeutralDayOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[22%] top-[20%] h-[58%] w-[52%] rounded border border-slate-300/40 bg-slate-500/5" />
      <div className="pointer-events-none absolute left-[24%] top-[17%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-slate-300">
        Neutral Day
      </div>
    </>
  );
}
