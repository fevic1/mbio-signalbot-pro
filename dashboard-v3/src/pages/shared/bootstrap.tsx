import { createRoot } from "react-dom/client";
import { useEffect, useState } from "react";
import "@/index.css";
import TerminalShell from "@/layouts/TerminalShell";
import { useAuth } from "@/store/auth";

function ProtectedApp({ Page }: { Page: React.ComponentType }) {
  const checkAuth = useAuth((s) => s.checkAuth);
  const status = useAuth((s) => s.status);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        await checkAuth();
      } finally {
        setReady(true);
      }
    })();
  }, [checkAuth]);

  useEffect(() => {
    if (!ready) return;

    if (status === "unauthenticated") {
      window.location.replace("/pages/login/");
    }
  }, [ready, status]);

  if (!ready || status === "checking") {
    return null;
  }

  return (
    <TerminalShell>
      <Page />
    </TerminalShell>
  );
}

export function bootstrap(Page: React.ComponentType) {
  createRoot(
    document.getElementById("root")!
  ).render(<ProtectedApp Page={Page} />);
}
