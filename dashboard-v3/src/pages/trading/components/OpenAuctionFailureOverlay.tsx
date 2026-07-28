export default function OpenAuctionFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[31%] top-[35%] h-[18%] w-[30%] rounded border border-red-500/60 bg-red-500/10" />
      <div className="pointer-events-none absolute left-[33%] top-[31%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Open Auction Failure
      </div>
    </>
  );
}
