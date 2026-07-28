import { useEffect } from "react";
import OverlayRenderer from "./OverlayRenderer";
import ChartInstance from "../chart/ChartInstance";
import { hydrateOverlayWorkspace } from "../overlays/state/hydrateWorkspace";
import OverlayControlPanel from "./overlays/OverlayControlPanel";
import OverlayPresetSelector from "./overlays/OverlayPresetSelector";

export default function ChartPanel() {

useEffect(() => {
  hydrateOverlayWorkspace();
}, []);

return (
  <div className="relative flex flex-1 overflow-hidden bg-black">

    <ChartInstance id="chart-1" />

    <OverlayRenderer />

    <OverlayControlPanel />

    <OverlayPresetSelector />

  </div>
);

}
