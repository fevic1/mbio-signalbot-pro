export default function InitialBalanceBreakoutOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[36%] top-[24%] h-[16%] w-[28%] rounded border border-cyan-400 border-dashed bg-cyan-500/10" />
      <div className="pointer-events-none absolute left-[50%] top-[24%] h-[46%] border-l-2 border-cyan-400" />
      <div className="pointer-events-none absolute left-[38%] top-[20%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-cyan-300">
        Initial Balance Breakout
      </div>
    </>
  );
}
