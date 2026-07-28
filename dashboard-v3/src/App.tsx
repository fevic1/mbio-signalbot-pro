import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import { useAuth } from "@/store/auth";
import { Login } from "@/components/Login";
import { Layout } from "@/components/Layout";

import Dashboard from "./Dashboard";
import { TradingPage } from "./pages/trading";
import MarketsPage from "./pages/Markets";
import AIPage from "./pages/AI";
import PortfolioPage from "./pages/Portfolio";
import SystemPage from "./pages/System";
import AIMemoryPage from "./pages/AI_Memory";

function App() {
  const { status, checkAuth } = useAuth();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  if (status === "checking") {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background text-sm text-muted-foreground">
        Checking session…
      </div>
    );
  }

  if (status === "unauthenticated") {
    return <Login />;
  }

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trading" element={<TradingPage />} />
        <Route path="/markets" element={<MarketsPage />} />
        <Route path="/ai" element={<AIPage />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/system" element={<SystemPage />} />
        <Route path="/ai-memory" element={<AIMemoryPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
