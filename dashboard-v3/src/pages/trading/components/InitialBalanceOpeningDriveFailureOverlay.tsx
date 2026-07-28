export default function InitialBalanceOpeningDriveFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[22%] h-[18%] border-l-2 border-red-400 border-dashed" />
      <div className="pointer-events-none absolute left-[40%] top-[18%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Initial Balance Opening Drive Failure
      </div>
    </>
  );
}
