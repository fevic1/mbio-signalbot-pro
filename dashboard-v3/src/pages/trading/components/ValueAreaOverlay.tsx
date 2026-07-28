export default function ValueAreaOverlay() {
  return (
    <div className="pointer-events-none absolute left-[22%] top-[30%] h-[34%] w-[56%] rounded border border-yellow-300/50 bg-yellow-300/5">
      <div className="absolute left-2 top-2 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-yellow-300">
        Value Area (VAH / VAL)
      </div>

      <div className="absolute inset-x-0 top-0 border-t border-yellow-300/60" />

      <div className="absolute inset-x-0 bottom-0 border-b border-yellow-300/60" />
    </div>
  );
}
