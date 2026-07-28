export default function PremiumDiscountOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-12 right-16 top-[50%] border-t border-dashed border-yellow-400/60">
        <div className="absolute right-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[10px] text-yellow-300">
          Equilibrium
        </div>
      </div>

      <div className="pointer-events-none absolute left-12 right-16 top-8 bottom-[50%] bg-red-500/5" />

      <div className="pointer-events-none absolute left-12 right-16 bottom-8 top-[50%] bg-green-500/5" />

      <div className="pointer-events-none absolute left-3 top-12 text-[10px] text-red-300">
        Premium
      </div>

      <div className="pointer-events-none absolute left-3 bottom-12 text-[10px] text-green-300">
        Discount
      </div>
    </>
  );
}
