import { createRoot } from "react-dom/client";
import "@/index.css";
import TerminalShell from "@/layouts/TerminalShell";

export function bootstrap(Page: React.ComponentType) {
  createRoot(
    document.getElementById("root")!
  ).render(
    <TerminalShell>
      <Page />
    </TerminalShell>
  );
}
