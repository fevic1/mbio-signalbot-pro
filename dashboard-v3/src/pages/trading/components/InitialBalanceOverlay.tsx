export default function InitialBalanceOverlay() {
  return (
    <div className="pointer-events-none absolute left-[14%] top-[24%] h-[42%] w-[13%] rounded border border-indigo-400/60 bg-indigo-500/10">
      <div className="absolute left-2 top-2 rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-indigo-300">
        Initial Balance
      </div>

      <div className="absolute inset-x-0 top-0 border-t border-indigo-300/70" />

      <div className="absolute inset-x-0 bottom-0 border-b border-indigo-300/70" />
    </div>
  );
}
