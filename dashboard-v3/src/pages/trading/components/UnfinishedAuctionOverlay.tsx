const auctions = [
  {
    top: "34%",
    label: "Unfinished Auction",
  },
  {
    top: "79%",
    label: "Unfinished Auction",
  },
];

export default function UnfinishedAuctionOverlay() {
  return (
    <>
      {auctions.map((auction, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: auction.top }}
        >
          <div className="border-t-2 border-yellow-400 border-dashed" />
          <div className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-yellow-300">
            {auction.label}
          </div>
        </div>
      ))}
    </>
  );
}
