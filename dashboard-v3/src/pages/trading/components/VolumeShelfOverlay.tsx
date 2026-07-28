const shelves = [
  {
    top: "27%",
    height: "9%",
  },
  {
    top: "63%",
    height: "10%",
  },
];

export default function VolumeShelfOverlay() {
  return (
    <>
      {shelves.map((shelf, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16 rounded border border-blue-300/40 bg-blue-400/10"
          style={{
            top: shelf.top,
            height: shelf.height,
          }}
        >
          <div className="absolute right-2 top-1 text-[9px] text-blue-300">
            Volume Shelf
          </div>
        </div>
      ))}
    </>
  );
}
