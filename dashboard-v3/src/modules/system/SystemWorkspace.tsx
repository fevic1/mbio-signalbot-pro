import { AiosRuntimePanel } from "./AiosRuntimePanel";
import { McpRegistryPanel } from "./McpRegistryPanel";

export function SystemWorkspace() {
  return (
    <div className="
  space-y-6
">

      <div>
        <h1 className="
          text-3xl
          font-bold
        ">
          AIOS Operations Center
        </h1>

        <p className="
          mt-2
          text-sm
          text-white/40
        ">
          Runtime health, agent services and MCP infrastructure
        </p>
      </div>

      <AiosRuntimePanel />

      <McpRegistryPanel />

    </div>
  );
}
