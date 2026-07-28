const poc = [
  {
    top: "46%",
    label: "POC",
  },
];

export default function POCOverlay() {
  return (
    <>
      {poc.map((line) => (
        <div
          key={line.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: line.top }}
        >
          <div className="border-t-2 border-yellow-400" />
          <div className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-yellow-300">
            {line.label}
          </div>
        </div>
      ))}
    </>
  );
}
