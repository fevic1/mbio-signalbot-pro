const pocs = [
  { top: "18%" },
  { top: "52%" },
  { top: "77%" },
];

export default function NakedPOCOverlay() {
  return (
    <>
      {pocs.map((poc, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: poc.top }}
        >
          <div className="border-t border-pink-400" />
          <div className="absolute right-2 -top-4 text-[9px] text-pink-300">
            Naked POC
          </div>
        </div>
      ))}
    </>
  );
}
