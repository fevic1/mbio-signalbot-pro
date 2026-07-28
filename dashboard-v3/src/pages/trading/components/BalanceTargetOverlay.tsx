const targets = [
  { top: "24%", label: "Balance High" },
  { top: "49%", label: "Balance Mid" },
  { top: "74%", label: "Balance Low" },
];

export default function BalanceTargetOverlay() {
  return (
    <>
      {targets.map((target) => (
        <div
          key={target.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: target.top }}
        >
          <div className="border-t border-violet-400 border-dashed" />
          <div className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-violet-300">
            {target.label}
          </div>
        </div>
      ))}
    </>
  );
}
