import { Plus } from "lucide-react";

interface Props {
  onClick?: () => void;
}

export default function CreateBotButton({ onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-2 rounded-lg bg-cyan-500 px-3 py-2 text-sm font-semibold text-black transition hover:bg-cyan-400"
    >
      <Plus className="h-4 w-4" />
      New Bot
    </button>
  );
}
