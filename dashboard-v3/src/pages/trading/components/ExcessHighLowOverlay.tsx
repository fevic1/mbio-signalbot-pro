const excess = [
  {
    top: "8%",
    label: "Buying Excess",
  },
  {
    top: "88%",
    label: "Selling Excess",
  },
];

export default function ExcessHighLowOverlay() {
  return (
    <>
      {excess.map((item) => (
        <div
          key={item.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: item.top }}
        >
          <div className="border-t-2 border-emerald-300 border-dotted" />
          <div className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-emerald-300">
            {item.label}
          </div>
        </div>
      ))}
    </>
  );
}
