export default function AcceptanceRejectionOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[24%] top-[29%] h-[18%] w-[20%] rounded border border-emerald-400/50 bg-emerald-500/10">
        <div className="absolute left-2 top-2 text-[9px] text-emerald-300">
          Acceptance
        </div>
      </div>

      <div className="pointer-events-none absolute left-[58%] top-[56%] h-[12%] w-[18%] rounded border border-red-400/50 bg-red-500/10">
        <div className="absolute left-2 top-2 text-[9px] text-red-300">
          Rejection
        </div>
      </div>
    </>
  );
}
