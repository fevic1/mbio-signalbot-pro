export default function OpenRejectionReverseOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[48%] top-[12%] h-[14%] border-l-2 border-red-400" />
      <div className="pointer-events-none absolute left-[44%] top-[26%] h-[28%] w-[18%] rounded-full border border-red-400/60" />
      <div className="pointer-events-none absolute left-[50%] top-[9%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        Open Rejection Reverse
      </div>
    </>
  );
}
