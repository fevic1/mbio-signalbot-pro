export default function InitialBalanceNeutralOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[24%] h-[34%] border-l border-yellow-300 border-dashed" />
      <div className="pointer-events-none absolute left-[35%] top-[40%] w-[30%] border-t border-yellow-300 border-dashed" />
      <div className="pointer-events-none absolute left-[39%] top-[18%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-yellow-300">
        Initial Balance Neutral
      </div>
    </>
  );
}
