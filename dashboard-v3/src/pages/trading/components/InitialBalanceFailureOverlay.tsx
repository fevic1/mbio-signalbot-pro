export default function InitialBalanceFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[36%] top-[24%] h-[16%] w-[28%] rounded border border-rose-400 border-dashed bg-rose-500/10" />
      <div className="pointer-events-none absolute left-[50%] top-[39%] h-[18%] border-l-2 border-rose-400" />
      <div className="pointer-events-none absolute left-[38%] top-[20%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-rose-300">
        Initial Balance Failure
      </div>
    </>
  );
}
