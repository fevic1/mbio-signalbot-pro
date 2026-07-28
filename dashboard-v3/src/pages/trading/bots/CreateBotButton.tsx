import { Plus } from "lucide-react";

interface CreateBotButtonProps {
  onClick?: () => void;
}

export default function CreateBotButton({
  onClick,
}: CreateBotButtonProps) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center justify-center gap-2 rounded-xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-3 text-sm font-semibold text-cyan-400 transition-all hover:border-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300 active:scale-[0.99]"
    >
      <Plus className="h-4 w-4" />
      Create Bot
    </button>
  );
}
