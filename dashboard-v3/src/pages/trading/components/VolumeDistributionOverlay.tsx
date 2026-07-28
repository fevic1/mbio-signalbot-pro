const bars = [24, 40, 62, 78, 54, 33, 48, 68, 44, 26];

export default function VolumeDistributionOverlay() {
  return (
    <div className="pointer-events-none absolute right-0 top-[10%] flex h-[72%] w-20 flex-col justify-between">
      {bars.map((width, index) => (
        <div
          key={index}
          className="h-3 rounded-l bg-sky-400/35"
          style={{ width: `${width}px` }}
        />
      ))}
    </div>
  );
}
