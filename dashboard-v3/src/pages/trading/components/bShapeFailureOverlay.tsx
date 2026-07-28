export default function BShapeFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[56%] top-[42%] h-[22%] w-[18%] rounded border border-red-500/50 bg-red-500/10" />
      <div className="pointer-events-none absolute left-[57%] top-[39%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        B-Shape Failure
      </div>
    </>
  );
}
