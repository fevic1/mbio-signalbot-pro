import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">Operational Dashboard</h2>
        <span className="text-xs px-2 py-1 rounded bg-green-500/10 text-green-500 border border-green-500/20">
          LIVE
        </span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">fixed@mbio.com</span>
        <Button variant="destructive" size="sm">
          EMERGENCY STOP
        </Button>
      </div>
    </header>
  );
}
