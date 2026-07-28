const sessions = [
  {
    left: "8%",
    width: "18%",
    label: "Asia",
    color: "bg-blue-500/5 border-blue-500/20",
  },
  {
    left: "33%",
    width: "22%",
    label: "London",
    color: "bg-yellow-500/5 border-yellow-500/20",
  },
  {
    left: "60%",
    width: "25%",
    label: "New York",
    color: "bg-purple-500/5 border-purple-500/20",
  },
];

export default function SessionRangeOverlay() {
  return (
    <>
      {sessions.map((session) => (
        <div
          key={session.label}
          className={`pointer-events-none absolute top-8 bottom-8 border ${session.color}`}
          style={{
            left: session.left,
            width: session.width,
          }}
        >
          <div className="absolute left-2 top-2 rounded bg-[#0b0f17]/90 px-2 py-1 text-[10px] text-white/50">
            {session.label}
          </div>
        </div>
      ))}
    </>
  );
}
