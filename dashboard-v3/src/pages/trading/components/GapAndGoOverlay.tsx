export default function GapAndGoOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[6%] h-[76%] border-l-2 border-cyan-400 border-dashed" />
      <div className="pointer-events-none absolute left-[51%] top-[4%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-cyan-300">
        Gap & Go
      </div>
    </>
  );
}
