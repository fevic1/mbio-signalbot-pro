export default function OpenDriveOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[49%] top-[10%] h-[68%] border-l-2 border-green-400 border-dashed" />
      <div className="pointer-events-none absolute left-[51%] top-[8%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-green-300">
        Open Drive
      </div>
    </>
  );
}
