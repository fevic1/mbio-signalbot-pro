import TradingHeader from "./components/TradingHeader";
import TradingSidebar from "./components/TradingSidebar";
import TradingCenter from "./components/TradingCenter";
import TradingRightDock from "./components/TradingRightDock";

export default function TradingPage() {
  return (
    <div className="flex flex-col flex-1 overflow-hidden bg-gray-950 text-white">
      <TradingHeader />

      <div className="flex flex-1 overflow-hidden">
        <TradingSidebar />

        <TradingCenter />

        <TradingRightDock />
      </div>
    </div>
  );
}
