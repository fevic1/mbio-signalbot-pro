import { Ticket, TicketContext } from "@/components/Ticket";
import { BotsMiniList } from "@/components/BotsMiniList";

interface TradingRightDockProps {
  ticketCtx: TicketContext;
  setTicketCtx: (ctx: TicketContext) => void;
  gridRefreshKey: number;
  triggerPositionRefresh: () => void;
  triggerGridRefresh: () => void;
  notify: (msg: string, isError?: boolean) => void;
}

export default function TradingRightDock({
  ticketCtx,
  setTicketCtx,
  gridRefreshKey,
  triggerPositionRefresh,
  triggerGridRefresh,
  notify,
}: TradingRightDockProps) {
  return (
    <div className="flex w-[380px] flex-col gap-3 overflow-hidden flex-shrink-0">
      {/* Builder Section - Ticket/QuickTicket - Independent scroll */}
      <div className="flex-[2] min-h-0 overflow-y-auto rounded-md border border-border bg-card">
        <Ticket
          context={ticketCtx}
          onClose={() => setTicketCtx(null)}
          onResult={(msg: string, err: boolean) => {
            notify(msg, err);
            if (!err) setTicketCtx(null);
          }}
          triggerRefresh={triggerPositionRefresh}
          triggerGridRefresh={triggerGridRefresh}
          onChooseBotType={(t: "grid" | "dca") =>
            setTicketCtx(
              t === "grid"
                ? { type: "open_grid" }
                : { type: "open_dca" }
            )
          }
          botsListProps={undefined}
        />
      </div>

      {/* Splitter Placeholder - Later draggable */}
      <div className="h-1 bg-border rounded-full flex-shrink-0" />

      {/* Bots Section - Independent scroll */}
      <div className="flex-1 min-h-0 overflow-y-auto rounded-md border border-border bg-card p-3">
        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Running Bots
        </div>

        <BotsMiniList
          refreshKey={gridRefreshKey}
          onCloseGrid={(asset: string) =>
            setTicketCtx({
              type: "close_grid",
              asset,
            })
          }
          onCloseDca={(asset: string) =>
            setTicketCtx({
              type: "close_dca",
              asset,
            })
          }
        />
      </div>

      {/* Create Bot Button */}
      <button
        className="h-11 rounded-md bg-primary font-medium text-primary-foreground hover:bg-primary/90 transition-colors flex-shrink-0"
        onClick={() =>
          setTicketCtx({
            type: "create_bot_choice",
          })
        }
      >
        + Create Bot
      </button>
    </div>
  );
}
