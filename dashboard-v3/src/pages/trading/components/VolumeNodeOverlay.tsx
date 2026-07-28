const nodes = [
  {
    top: "18%",
    height: "12%",
    width: "7%",
  },
  {
    top: "41%",
    height: "18%",
    width: "10%",
  },
  {
    top: "68%",
    height: "11%",
    width: "6%",
  },
];

export default function VolumeNodeOverlay() {
  return (
    <div className="pointer-events-none absolute right-14 top-0 bottom-0 w-16">
      {nodes.map((node, index) => (
        <div
          key={index}
          className="absolute right-0 rounded-l bg-cyan-400/30 border border-cyan-300/40"
          style={{
            top: node.top,
            height: node.height,
            width: node.width,
          }}
        />
      ))}
    </div>
  );
}
