export default function InitialBalanceOpeningAuctionFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[42%] top-[28%] h-[18%] w-[16%] rounded border border-red-400 border-dashed bg-red-500/10" />
      <div className="pointer-events-none absolute left-[32%] top-[18%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Initial Balance Opening Auction Failure
      </div>
    </>
  );
}
