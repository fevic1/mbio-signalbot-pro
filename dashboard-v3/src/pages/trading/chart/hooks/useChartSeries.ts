
import {
  ISeriesApi,
  CandlestickSeries,
} from "lightweight-charts";

import {
  useEffect,
  useRef,
} from "react";

import { Candle } from "../../market/state/marketStore";


export function useChartSeries(
  chart:any,
  candles:Candle[]
){

const seriesRef =
useRef<ISeriesApi<"Candlestick"> | null>(null);


useEffect(()=>{

if(!chart){
 return;
}


if(seriesRef.current){
 return;
}


const series =
chart.addSeries(
 CandlestickSeries
);


seriesRef.current = series;


// IMPORTANT:
// Do not remove series here.
// lightweight-charts handles lifecycle internally.


},[
chart
]);


useEffect(()=>{

const series =
seriesRef.current;


if(!series){
 return;
}


if(!candles.length){
 return;
}


series.setData(
 candles.map(c=>({

 time:c.time as any,

 open:c.open,

 high:c.high,

 low:c.low,

 close:c.close

 }))
);


},[
candles
]);


return seriesRef;

}
