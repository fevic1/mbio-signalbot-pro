export default function InitialBalanceValueRejectionOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[42%] top-[30%] h-[18%] w-[18%] rounded border border-rose-400 border-dashed bg-rose-500/10" />
      <div className="pointer-events-none absolute left-[35%] top-[18%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-rose-300">
        Initial Balance Value Rejection
      </div>
    </>
  );
}
