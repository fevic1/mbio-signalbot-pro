import { useState } from "react";

import StrategySelector from "./StrategySelector";
import QuickTicket from "./QuickTicket";

type Builder =
  | "selector"
  | "quick-ticket"
  | "grid"
  | "dca";

export default function BuilderRouter() {
  const [builder, setBuilder] = useState<Builder>("selector");

  switch (builder) {
    case "quick-ticket":
      return (
        <QuickTicket
          onBack={() => setBuilder("selector")}
        />
      );

    case "grid":
      return (
        <div className="p-5 text-white/50">
          Grid Builder (Coming Soon)
        </div>
      );

    case "dca":
      return (
        <div className="p-5 text-white/50">
          DCA Builder (Coming Soon)
        </div>
      );

    default:
      return (
        <StrategySelector
          onQuickTicket={() => setBuilder("quick-ticket")}
          onGrid={() => setBuilder("grid")}
          onDCA={() => setBuilder("dca")}
        />
      );
  }
}
