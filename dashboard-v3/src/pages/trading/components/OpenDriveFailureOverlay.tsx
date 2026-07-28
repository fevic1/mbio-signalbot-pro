export default function OpenDriveFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[10%] h-[16%] border-l-2 border-orange-400 border-dashed" />
      <div className="pointer-events-none absolute left-[38%] top-[27%] h-[18%] w-[26%] rounded border border-orange-400/60 bg-orange-500/10" />
      <div className="pointer-events-none absolute left-[51%] top-[8%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-orange-300">
        Open Drive Failure
      </div>
    </>
  );
}
