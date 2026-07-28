const bars = [15, 22, 28, 35, 41, 52, 64, 58, 49, 36, 24, 17];

export default function VolumeProfile() {
  return (
    <div className="pointer-events-none absolute right-16 top-8 bottom-8 z-10 flex w-16 flex-col justify-center gap-[2px]">
      {bars.map((width, index) => (
        <div
          key={index}
          className="ml-auto h-3 rounded-l bg-cyan-400/20"
          style={{ width: `${width}px` }}
        />
      ))}
    </div>
  );
}
