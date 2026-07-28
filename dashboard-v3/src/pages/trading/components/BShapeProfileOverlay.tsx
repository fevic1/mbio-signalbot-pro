export default function BShapeProfileOverlay() {
  return (
    <div className="pointer-events-none absolute right-6 top-[18%] flex h-[58%] w-20 flex-col justify-between">
      <div className="h-24 w-16 rounded-l-full bg-blue-400/30" />
      <div className="h-8 w-5 self-end bg-blue-300/40" />
      <div className="h-24 w-16 rounded-l-full bg-blue-400/30" />
      <div className="absolute -left-12 top-0 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-blue-300">
        B-Shape
      </div>
    </div>
  );
}
