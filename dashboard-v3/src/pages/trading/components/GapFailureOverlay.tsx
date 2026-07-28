export default function GapFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[40%] top-[12%] h-[18%] w-[22%] rounded border border-red-500 border-dashed bg-red-500/10" />
      <div className="pointer-events-none absolute left-[43%] top-[8%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Gap Failure
      </div>
    </>
  );
}
