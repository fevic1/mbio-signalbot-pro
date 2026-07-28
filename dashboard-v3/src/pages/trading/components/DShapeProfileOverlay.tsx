export default function DShapeProfileOverlay() {
  return (
    <div className="pointer-events-none absolute right-6 top-[20%] flex h-[50%] w-20 items-center justify-end">
      <div className="h-full w-16 rounded-full border border-cyan-400/50 bg-cyan-500/15" />
      <div className="absolute -left-10 top-0 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-cyan-300">
        D-Shape
      </div>
    </div>
  );
}
