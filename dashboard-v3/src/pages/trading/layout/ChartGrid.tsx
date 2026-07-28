import { useLayoutStore } from "./state/layoutStore";
import { useChartStore } from "../chart/state/chartStore";
import ChartInstance from "../chart/ChartInstance";

export default function ChartGrid() {

  const charts = useChartStore(
    state => state.charts
  );

  const mode = useLayoutStore(
    state => state.mode
  );

  const count =
    mode === "single"
      ? 1
      : mode === "double"
      ? 2
      : 4;

  return (
    <div
      className={`
        grid h-full w-full gap-2
        ${
          mode === "quad"
            ? "grid-cols-2 grid-rows-2"
            : mode === "double"
            ? "grid-cols-2"
            : "grid-cols-1"
        }
      `}
    >
      {charts
        .slice(0, count)
        .map(chart => (
          <ChartInstance
            key={chart.id}
            id={chart.id}
          />
        ))}
    </div>
  );
}
