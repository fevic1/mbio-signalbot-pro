export default function CrosshairHUD() {
  return (
    <>
      <div className="pointer-events-none absolute left-1/2 top-0 z-20 h-full w-px -translate-x-1/2 bg-cyan-400/40" />

      <div className="pointer-events-none absolute left-0 top-1/2 z-20 h-px w-full -translate-y-1/2 bg-cyan-400/40" />

      <div className="pointer-events-none absolute left-1/2 top-1/2 z-30 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400 bg-cyan-400/20" />

      <div className="pointer-events-none absolute left-3 top-1/2 z-30 -translate-y-1/2 rounded border border-white/10 bg-[#0b0f17]/95 px-2 py-1 text-[11px] text-white">
        118,462.30
      </div>

      <div className="pointer-events-none absolute bottom-3 left-1/2 z-30 -translate-x-1/2 rounded border border-white/10 bg-[#0b0f17]/95 px-2 py-1 text-[11px] text-white">
        2026-07-27&nbsp;&nbsp;08:15
      </div>
    </>
  );
}
