import { useState } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, Search, Save, Play, BarChart3 } from 'lucide-react';

interface QTParametersPanelProps {
  onDeploy?: () => void;
}

interface AccordionSectionProps {
  title: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

function AccordionSection({ title, defaultOpen = false, children }: AccordionSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-border/50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-muted/50 transition-colors"
      >
        <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
        <ChevronDown
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform duration-200",
            isOpen && "rotate-180"
          )}
        />
      </button>
      {isOpen && <div className="px-4 pb-4 space-y-3">{children}</div>}
    </div>
  );
}

function FormField({ label, value, type = "text" }: { label: string; value: string; type?: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <label className="text-xs text-muted-foreground whitespace-nowrap">{label}</label>
      <input
        type={type}
        defaultValue={value}
        className="w-24 rounded border border-border bg-background px-2 py-1 text-xs text-foreground text-right focus:outline-none focus:ring-1 focus:ring-primary"
      />
    </div>
  );
}

export function QTParametersPanel({ onDeploy }: QTParametersPanelProps) {
  return (
    <div className="flex h-full flex-col bg-card border-l border-border">
      {/* Sticky Header */}
      <div className="sticky-header flex items-center justify-between px-4 py-3 border-b border-border">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
          QT Parameters
        </h3>
        <button className="text-muted-foreground hover:text-foreground transition-colors">
          <Search className="h-4 w-4" />
        </button>
      </div>

      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <AccordionSection title="General Settings" defaultOpen={true}>
          <FormField label="Strategy Name" value="AIOS QT Strategy" />
          <div className="flex items-center justify-between gap-4">
            <label className="text-xs text-muted-foreground">Timeframe</label>
            <select className="w-24 rounded border border-border bg-background px-2 py-1 text-xs text-foreground text-right focus:outline-none focus:ring-1 focus:ring-primary">
              <option>1 Hour</option>
              <option>4 Hours</option>
              <option>1 Day</option>
            </select>
          </div>
        </AccordionSection>

        <AccordionSection title="Risk Settings" defaultOpen={true}>
          <FormField label="Risk Per Trade (%)" value="1.00" type="number" />
          <FormField label="Max Drawdown (%)" value="15.00" type="number" />
          <FormField label="Max Daily Loss (%)" value="5.00" type="number" />
          <div className="flex items-center justify-between gap-4">
            <label className="text-xs text-muted-foreground">Leverage</label>
            <select className="w-24 rounded border border-border bg-background px-2 py-1 text-xs text-foreground text-right focus:outline-none focus:ring-1 focus:ring-primary">
              <option>5x</option>
              <option>10x</option>
              <option>20x</option>
            </select>
          </div>
        </AccordionSection>

        <AccordionSection title="Entry Conditions" defaultOpen={false}>
          <FormField label="RSI Period" value="14" type="number" />
          <FormField label="RSI Oversold" value="30" type="number" />
          <FormField label="RSI Overbought" value="70" type="number" />
        </AccordionSection>

        <AccordionSection title="Exit Conditions" defaultOpen={false}>
          <FormField label="Take Profit (%)" value="2.50" type="number" />
          <FormField label="Stop Loss (%)" value="1.00" type="number" />
        </AccordionSection>
      </div>

      {/* Sticky Footer */}
      <div className="sticky-footer px-4 py-3 border-t border-border space-y-2">
        <button className="w-full flex items-center justify-center gap-2 h-9 rounded bg-primary font-medium text-primary-foreground hover:bg-primary/90 transition-colors text-xs">
          <Save className="h-3 w-3" />
          Save Parameters
        </button>
        <div className="flex gap-2">
          <button className="flex-1 flex items-center justify-center gap-2 h-9 rounded bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors text-xs">
            <BarChart3 className="h-3 w-3" />
            Backtest
          </button>
          <button 
            onClick={onDeploy}
            className="flex-1 flex items-center justify-center gap-2 h-9 rounded bg-emerald-600 text-white hover:bg-emerald-700 transition-colors text-xs"
          >
            <Play className="h-3 w-3" />
            Deploy
          </button>
        </div>
      </div>
    </div>
  );
}
