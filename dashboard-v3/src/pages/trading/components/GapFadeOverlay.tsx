export default function GapFadeOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[35%] top-[12%] h-[18%] w-[28%] rounded border border-red-400 border-dashed bg-red-500/10" />
      <div className="pointer-events-none absolute left-[38%] top-[8%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Gap Fade
      </div>
    </>
  );
}
