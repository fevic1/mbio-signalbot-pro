export default function InitialBalanceRejectionOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[35%] top-[24%] h-[18%] w-[30%] rounded border border-red-400 border-dashed bg-red-500/10" />
      <div className="pointer-events-none absolute left-[38%] top-[20%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Initial Balance Rejection
      </div>
    </>
  );
}
