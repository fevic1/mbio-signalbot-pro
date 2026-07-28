const prices = [
  "118,700",
  "118,650",
  "118,600",
  "118,550",
  "118,500",
  "118,450",
  "118,400",
  "118,350",
  "118,300",
];

export default function PriceScale() {
  return (
    <div className="absolute inset-y-0 right-0 z-20 flex w-16 flex-col justify-between border-l border-white/10 bg-[#090d14]/80 py-4 backdrop-blur-sm">
      {prices.map((price) => (
        <div
          key={price}
          className="pr-2 text-right text-[11px] font-medium text-white/45"
        >
          {price}
        </div>
      ))}
    </div>
  );
}
