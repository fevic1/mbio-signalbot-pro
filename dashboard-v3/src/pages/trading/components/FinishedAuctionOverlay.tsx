const auctions = [
  {
    top: "22%",
    label: "Finished Auction",
  },
  {
    top: "66%",
    label: "Finished Auction",
  },
];

export default function FinishedAuctionOverlay() {
  return (
    <>
      {auctions.map((auction, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: auction.top }}
        >
          <div className="border-t-2 border-lime-400" />
          <div className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-lime-300">
            {auction.label}
          </div>
        </div>
      ))}
    </>
  );
}
