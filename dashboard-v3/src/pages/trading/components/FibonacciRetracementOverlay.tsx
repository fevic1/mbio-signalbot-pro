const levels = [
  { top: "24%", label: "0.0" },
  { top: "35%", label: "0.236" },
  { top: "44%", label: "0.382" },
  { top: "50%", label: "0.5" },
  { top: "57%", label: "0.618" },
  { top: "66%", label: "0.786" },
  { top: "77%", label: "1.0" },
];

export default function FibonacciRetracementOverlay() {
  return (
    <>
      {levels.map((level) => (
        <div
          key={level.label}
          className="pointer-events-none absolute left-12 right-16 border-t border-amber-300/25"
          style={{ top: level.top }}
        >
          <span className="absolute right-2 -top-4 text-[9px] text-amber-300">
            {level.label}
          </span>
        </div>
      ))}
    </>
  );
}
