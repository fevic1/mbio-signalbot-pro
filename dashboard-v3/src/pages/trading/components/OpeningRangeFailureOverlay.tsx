export default function OpeningRangeFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[34%] top-[21%] h-[18%] w-[32%] rounded border border-red-400 border-dashed bg-red-500/10" />
      <div className="pointer-events-none absolute left-[48%] top-[38%] h-[20%] border-l-2 border-red-400" />
      <div className="pointer-events-none absolute left-[36%] top-[17%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Opening Range Failure
      </div>
    </>
  );
}
