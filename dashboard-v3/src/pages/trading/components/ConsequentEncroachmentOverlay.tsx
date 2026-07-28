const levels = [
  {
    top: "37%",
    left: "41%",
    width: "11%",
  },
  {
    top: "59%",
    left: "62%",
    width: "10%",
  },
];

export default function ConsequentEncroachmentOverlay() {
  return (
    <>
      {levels.map((level, index) => (
        <div
          key={index}
          className="pointer-events-none absolute"
          style={{
            top: level.top,
            left: level.left,
            width: level.width,
          }}
        >
          <div className="border-t-2 border-cyan-300" />
          <div className="mt-1 text-center text-[9px] text-cyan-300">
            CE
          </div>
        </div>
      ))}
    </>
  );
}
