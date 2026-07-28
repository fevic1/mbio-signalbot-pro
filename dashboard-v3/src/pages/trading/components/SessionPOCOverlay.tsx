const sessions = [
  { top: "16%", color: "cyan", label: "Asia POC" },
  { top: "42%", color: "emerald", label: "London POC" },
  { top: "69%", color: "orange", label: "New York POC" },
];

export default function SessionPOCOverlay() {
  return (
    <>
      {sessions.map((session) => (
        <div
          key={session.label}
          className="pointer-events-none absolute left-12 right-16"
          style={{ top: session.top }}
        >
          <div className="border-t border-dotted border-cyan-300" />
          <div className="absolute left-2 -top-4 rounded bg-[#0b0f17]/90 px-2 py-0.5 text-[9px] text-cyan-300">
            {session.label}
          </div>
        </div>
      ))}
    </>
  );
}
