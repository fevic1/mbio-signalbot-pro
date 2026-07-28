export default function OpenAuctionOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[30%] top-[34%] h-[20%] w-[38%] rounded border border-cyan-400 border-dashed bg-cyan-500/10" />
      <div className="pointer-events-none absolute left-[33%] top-[31%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-cyan-300">
        Open Auction
      </div>
    </>
  );
}
