import { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown, Search, Save, BarChart3, TrendingUp } from 'lucide-react';
import { fetchWithAuth } from '@/lib/apiClient';
import { QuickTicket } from '@/modules/trading/QuickTicket';

interface QTParametersPanelProps {
  onDeploy?: () => void;
  selectedAsset?: string;
  onAssetSelect?: (asset: string) => void;
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

export function QTParametersPanel({ selectedAsset, onAssetSelect }: QTParametersPanelProps) {
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  const [isLoadingAssets, setIsLoadingAssets] = useState(false);

  // Fetch available assets for selector
  useEffect(() => {
    const fetchAssets = async () => {
      setIsLoadingAssets(true);
      try {
        const data = await fetchWithAuth<string[]>('/api/dashboard/assets', {
          timeout: 5000,
          retries: 2,
          backoffMs: 1000,
        });
        if (data && Array.isArray(data)) {
          setAvailableAssets(data.slice(0, 50));
          if (!selectedAsset && data.length > 0 && onAssetSelect) {
            onAssetSelect(data[0]);
          }
        }
      } catch (err) {
        console.error('[QT Parameters] Failed to fetch assets:', err);
      } finally {
        setIsLoadingAssets(false);
      }
    };

    fetchAssets();
  }, [selectedAsset, onAssetSelect]);

  return (
    <div className="flex h-full flex-col bg-card border-l border-border overflow-hidden">
      {/* Asset Selector Bar - Fixed height */}
      <div className="px-4 py-3 border-b border-border bg-muted/30 flex-shrink-0">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-foreground">
            Trading Asset
          </span>
          <TrendingUp className="h-3 w-3 text-primary" />
        </div>
        <select
          value={selectedAsset || ''}
          onChange={(e) => onAssetSelect?.(e.target.value)}
          disabled={isLoadingAssets}
          className="w-full rounded border border-border bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
        >
          {isLoadingAssets ? (
            <option>Loading...</option>
          ) : (
            availableAssets.map(asset => (
              <option key={asset} value={asset}>
                {asset}/USDT
              </option>
            ))
          )}
        </select>
      </div>

      {/* Header - Fixed height */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border flex-shrink-0">
        <h3 className="text-xs font-bold uppercase tracking-wider text-foreground">
          QT Parameters
        </h3>
        <button className="text-muted-foreground hover:text-foreground transition-colors">
          <Search className="h-4 w-4" />
        </button>
      </div>

      {/* Scrollable Content - Constrained height */}
      <div className="flex-1 overflow-y-auto min-h-0">
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

      {/* Execution Footer - ALWAYS VISIBLE, fixed height */}
      <div className="px-4 py-3 border-t border-border bg-muted/30 flex-shrink-0 space-y-2">
        <button className="w-full flex items-center justify-center gap-2 h-9 rounded bg-primary font-medium text-primary-foreground hover:bg-primary/90 transition-colors text-xs">
          <Save className="h-3 w-3" />
          Save Parameters
        </button>
        <div className="flex gap-2">
          <button className="flex-1 flex items-center justify-center gap-2 h-9 rounded bg-secondary text-secondary-foreground hover:bg-secondary/80 transition-colors text-xs">
            <BarChart3 className="h-3 w-3" />
            Backtest
          </button>
          <div className="flex-1">
            <QuickTicket initialAsset={selectedAsset} />
          </div>
        </div>
      </div>
    </div>
  );
}
