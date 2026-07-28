export type TicketContext = {
  type: "open_dca" | "close_position" | "open_grid" | "close_grid" | "close_dca" | "create_bot_choice" | "close_all";
  asset?: string;
  side?: string;
  size?: number;
} | null;

interface TicketProps {
  context: TicketContext;
  onClose: () => void;
  onResult: (msg: string, err: boolean) => void;
  triggerRefresh: () => void;
  triggerGridRefresh: () => void;
  onChooseBotType: (type: "grid" | "dca") => void;
  botsListProps: any;
}

export function Ticket({ 
  context, 
  onClose, 
  onChooseBotType,
}: TicketProps) {
  // Show bot type selection by default when context is null
  if (!context) {
    return (
      <div className="flex flex-col h-full p-4 space-y-3">
        <div className="mb-2">
          <h3 className="text-lg font-semibold">Select Bot Type</h3>
          <p className="text-sm text-muted-foreground mt-1">Choose a strategy to configure</p>
        </div>
        <button 
          onClick={() => onChooseBotType("dca")} 
          className="w-full p-4 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-md text-left transition-colors"
        >
          <div className="font-semibold">DCA Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Dollar Cost Averaging with dynamic sizing</div>
        </button>
        <button 
          onClick={() => onChooseBotType("grid")} 
          className="w-full p-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border rounded-md text-left transition-colors"
        >
          <div className="font-semibold">Grid Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Range-bound market making</div>
        </button>
      </div>
    );
  }

  // Bot Creation Choice
  if (context.type === "create_bot_choice") {
    return (
      <div className="flex flex-col h-full p-4 space-y-3">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold">Create Bot</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-xl leading-none">✕</button>
        </div>
        <p className="text-sm text-muted-foreground">Select bot type to configure:</p>
        <button 
          onClick={() => onChooseBotType("dca")} 
          className="w-full p-4 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-md text-left transition-colors"
        >
          <div className="font-semibold">DCA Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Dollar Cost Averaging with dynamic sizing</div>
        </button>
        <button 
          onClick={() => onChooseBotType("grid")} 
          className="w-full p-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border rounded-md text-left transition-colors"
        >
          <div className="font-semibold">Grid Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Range-bound market making</div>
        </button>
        <button onClick={onClose} className="w-full p-2 text-sm text-muted-foreground hover:text-foreground mt-auto">Cancel</button>
      </div>
    );
  }

  // Placeholder for other actions (close position, etc.)
  return (
    <div className="flex flex-col h-full p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold capitalize">{context.type.replace("_", " ")}</h3>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-xl leading-none">✕</button>
      </div>
      <div className="flex-1 flex items-center justify-center text-sm text-muted-foreground">
        Action: {context.type}
        {context.asset && <span className="ml-2">({context.asset})</span>}
      </div>
    </div>
  );
}
