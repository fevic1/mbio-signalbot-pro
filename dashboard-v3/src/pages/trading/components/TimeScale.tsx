const times = [
  "08:00",
  "08:15",
  "08:30",
  "08:45",
  "09:00",
  "09:15",
  "09:30",
  "09:45",
  "10:00",
];

export default function TimeScale() {
  return (
    <div className="absolute inset-x-0 bottom-0 z-20 flex h-8 items-center justify-between border-t border-white/10 bg-[#090d14]/80 px-8 backdrop-blur-sm">
      {times.map((time) => (
        <span
          key={time}
          className="text-[11px] font-medium text-white/40"
        >
          {time}
        </span>
      ))}
    </div>
  );
}
