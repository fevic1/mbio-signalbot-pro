import { useState } from 'react';
import DCABuilder from '@/pages/trading/builder/DCABuilder';
import GridBuilder from '@/pages/trading/builder/GridBuilder';

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
  selectedAsset?: string;
}

export function Ticket({ 
  context, 
  onClose, 
  onChooseBotType,
  selectedAsset,
}: TicketProps) {
  const [builderView, setBuilderView] = useState<'choice' | 'dca' | 'grid' | null>(null);

  // Show bot type selection by default when context is null
  if (!context) {
    return (
      <div className="flex flex-col h-full p-4 space-y-3">
        <div className="mb-2">
          <h3 className="text-lg font-semibold">Select Bot Type</h3>
          <p className="text-sm text-muted-foreground mt-1">Choose a strategy to configure</p>
        </div>
        <button 
          onClick={() => {
            setBuilderView('dca');
            onChooseBotType("dca");
          }}
          className="w-full p-4 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-md text-left transition-colors"
        >
          <div className="font-semibold">DCA Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Dollar Cost Averaging with dynamic sizing</div>
        </button>
        <button 
          onClick={() => {
            setBuilderView('grid');
            onChooseBotType("grid");
          }}
          className="w-full p-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border rounded-md text-left transition-colors"
        >
          <div className="font-semibold">Grid Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Range-bound market making</div>
        </button>
      </div>
    );
  }

  // Bot Creation Choice - Show actual choice UI
  if (context.type === "create_bot_choice" || builderView === 'choice') {
    return (
      <div className="flex flex-col h-full p-4 space-y-3">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold">Create Bot</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-xl leading-none">✕</button>
        </div>
        <p className="text-sm text-muted-foreground">Select bot type to configure:</p>
        <button 
          onClick={() => {
            setBuilderView('dca');
            onChooseBotType("dca");
          }}
          className="w-full p-4 bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 rounded-md text-left transition-colors"
        >
          <div className="font-semibold">DCA Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Dollar Cost Averaging with dynamic sizing</div>
        </button>
        <button 
          onClick={() => {
            setBuilderView('grid');
            onChooseBotType("grid");
          }}
          className="w-full p-4 bg-secondary hover:bg-secondary/80 text-secondary-foreground border border-border rounded-md text-left transition-colors"
        >
          <div className="font-semibold">Grid Bot</div>
          <div className="text-xs text-muted-foreground mt-1">Range-bound market making</div>
        </button>
        <button onClick={onClose} className="w-full p-2 text-sm text-muted-foreground hover:text-foreground mt-auto">Cancel</button>
      </div>
    );
  }

  // Render DCA Builder
  if (context.type === "open_dca" || builderView === 'dca') {
    return (
      <div className="flex flex-col h-full">
        <div className="flex justify-between items-center px-4 py-3 border-b border-border">
          <h3 className="text-sm font-semibold">DCA Configuration</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-lg leading-none">✕</button>
        </div>
        <DCABuilder 
          onContinue={() => {
            // In production: proceed to risk review, then execution
            alert(`DCA Bot configured for ${selectedAsset || 'BTC'}`);
            onClose();
          }}
        />
      </div>
    );
  }

  // Render Grid Builder
  if (context.type === "open_grid" || builderView === 'grid') {
    return (
      <div className="flex flex-col h-full">
        <div className="flex justify-between items-center px-4 py-3 border-b border-border">
          <h3 className="text-sm font-semibold">Grid Configuration</h3>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-lg leading-none">✕</button>
        </div>
        <GridBuilder 
          onContinue={() => {
            // In production: proceed to risk review, then execution
            alert(`Grid Bot configured for ${selectedAsset || 'BTC'}`);
            onClose();
          }}
        />
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
