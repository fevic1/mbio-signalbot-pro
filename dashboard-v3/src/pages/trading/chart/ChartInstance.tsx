import { useChartStore } from "./state/chartStore";
import { useMarketData } from "../market/hooks/useMarketData";
import CandlestickChart from "./components/CandlestickChart";

export default function ChartInstance({
id
}:{
id:string
}){

const chart =
useChartStore(
state=>state.charts.find(x=>x.id===id)
);


const candles =
useMarketData(
chart?.symbol ?? "BTC-PERP"
);


if(!chart){
return null;
}


return (

<div className="flex h-full flex-col rounded border border-white/10 bg-black">

<div className="flex justify-between border-b border-white/10 p-2 text-xs text-white">

<span>
{chart.symbol}
</span>

<span>
{chart.timeframe}
</span>

</div>


<div className="flex flex-1 overflow-hidden">

<CandlestickChart
candles={candles}
/>

</div>


</div>

);

}
