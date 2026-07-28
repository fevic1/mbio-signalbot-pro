export default function OpenRejectionReverseFailureOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[44%] top-[20%] h-[24%] w-[18%] rounded border border-red-500/50 bg-red-500/10" />
      <div className="pointer-events-none absolute left-[46%] top-[17%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-red-300">
        ORR Failure
      </div>
    </>
  );
}
