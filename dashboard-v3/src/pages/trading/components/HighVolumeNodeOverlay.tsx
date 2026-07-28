const nodes = [
  {
    top: "21%",
    height: "16%",
    width: "100%",
  },
  {
    top: "47%",
    height: "22%",
    width: "100%",
  },
];

export default function HighVolumeNodeOverlay() {
  return (
    <>
      {nodes.map((node, index) => (
        <div
          key={index}
          className="pointer-events-none absolute left-12 right-16 rounded bg-emerald-500/10 border border-emerald-400/40"
          style={{
            top: node.top,
            height: node.height,
          }}
        >
          <div className="absolute right-2 top-1 text-[9px] text-emerald-300">
            HVN
          </div>
        </div>
      ))}
    </>
  );
}
