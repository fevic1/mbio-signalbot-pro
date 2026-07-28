const rows = Array.from({ length: 16 });

export default function TPOLettersOverlay() {
  return (
    <div className="pointer-events-none absolute right-16 top-[12%] w-24">
      {rows.map((_, row) => (
        <div
          key={row}
          className="flex h-4 items-center gap-[2px] text-[8px] font-mono text-cyan-300/70"
        >
          {"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            .slice(0, 12)
            .split("")
            .map((c) => (
              <span key={c}>{c}</span>
            ))}
        </div>
      ))}
    </div>
  );
}
