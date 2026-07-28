export default function PShapeFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[24%] top-[30%] h-[20%] w-[18%] rounded border border-yellow-400/50 bg-yellow-500/10" />
      <div className="pointer-events-none absolute left-[25%] top-[27%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-yellow-300">
        P-Shape Failure
      </div>
    </>
  );
}
