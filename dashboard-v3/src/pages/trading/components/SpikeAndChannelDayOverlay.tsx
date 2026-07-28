export default function SpikeAndChannelDayOverlay() {
  return (
    <>
      <div className="pointer-events-none absolute left-[48%] top-[8%] h-[18%] border-l-4 border-sky-400" />
      <div className="pointer-events-none absolute left-[48%] top-[26%] h-[52%] w-[18%] -skew-x-6 border-l-2 border-r-2 border-sky-400/60 bg-sky-500/10" />
      <div className="pointer-events-none absolute left-[50%] top-[5%] rounded bg-[#0b0f17]/90 px-2 py-1 text-[9px] text-sky-300">
        Spike & Channel Day
      </div>
    </>
  );
}
