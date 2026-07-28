export default function MeasuringGapOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[12%] h-[54%] border-l-2 border-indigo-400 border-dashed" />
      <div className="pointer-events-none absolute left-[52%] top-[10%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-indigo-300">
        Measuring Gap
      </div>
    </>
  );
}
