import { TrendingUp } from "lucide-react";
import { RegimePanel } from "@/modules/markets/RegimePanel";
import AssetsTable from "@/modules/markets/AssetsTable";

export default function MarketsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <TrendingUp className="h-7 w-7 text-primary" />
        <h1 className="text-2xl font-bold">Market Intelligence</h1>
      </div>

      {/* Top: Deep Analysis for Selected Asset */}
      <div className="grid gap-6 lg:grid-cols-1">
        <RegimePanel defaultAsset="BTC" />
      </div>

      {/* Bottom: Broad Universe Scanning */}
      <div className="grid gap-6 lg:grid-cols-1">
        <AssetsTable />
      </div>
    </div>
  );
}
