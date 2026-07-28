export default function PShapeProfileOverlay() {
  return (
    <div className="pointer-events-none absolute right-6 top-[16%] flex h-[60%] w-20 flex-col items-end">
      <div className="h-24 w-16 rounded-r-full bg-emerald-400/30" />
      <div className="h-24 w-4 bg-emerald-300/40" />
      <div className="absolute -left-10 top-0 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-emerald-300">
        P-Shape
      </div>
    </div>
  );
}
