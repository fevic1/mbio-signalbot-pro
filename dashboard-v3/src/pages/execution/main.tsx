import { createRoot } from "react-dom/client";
import "@/index.css";

function App() {
  return (
    <div>
      <h1>MBIO SignalPro execution</h1>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
