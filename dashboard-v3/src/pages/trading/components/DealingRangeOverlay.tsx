export default function DealingRangeOverlay() {
  return (
    <div className="pointer-events-none absolute left-[19%] top-[20%] h-[58%] w-[60%] rounded border-2 border-dashed border-cyan-400/40">
      <div className="absolute left-2 top-2 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] font-semibold text-cyan-300">
        Dealing Range
      </div>

      <div className="absolute left-0 right-0 top-1/2 border-t border-cyan-300/25" />

      <div className="absolute right-2 top-[22%] text-[9px] text-cyan-300">
        Premium
      </div>

      <div className="absolute right-2 bottom-[22%] text-[9px] text-cyan-300">
        Discount
      </div>

      <div className="absolute right-2 top-[49%] text-[9px] text-cyan-300">
        Equilibrium
      </div>
    </div>
  );
}
