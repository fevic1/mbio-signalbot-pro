export default function OpenAuctionRejectionOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[34%] top-[30%] h-[22%] w-[34%] rounded border border-rose-400 border-dashed bg-rose-500/10" />
      <div className="pointer-events-none absolute left-[37%] top-[27%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-rose-300">
        Open Auction Rejection
      </div>
    </>
  );
}
