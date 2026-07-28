import { safeRemoveSeries } from "./safeRemoveSeries";
import {
  IChartApi,
  ISeriesApi,
  HistogramSeries,
} from "lightweight-charts";

import {
  Candle
} from "../../market/state/marketStore";

import {
  ChartOverlay
} from "./OverlayBridge";


export class VolumeProfileOverlay implements ChartOverlay {

private series?:ISeriesApi<"Histogram">;

private chart?:IChartApi;


constructor(
private candles:Candle[]
){}


attach(chart:IChartApi){

this.chart=chart;


this.series =
chart.addSeries(
HistogramSeries,
{
priceFormat:{
type:"volume"
}
}
);


this.render();

}


update(candles:Candle[]){

this.candles=candles;

this.render();

}


private render(){

if(!this.series){
return;
}


const distribution:
Record<string,number>={};


this.candles.forEach(candle=>{

const price =
(
candle.high+
candle.low+
candle.close
)/3;


const key =
price.toFixed(2);


distribution[key] =
(distribution[key] ?? 0)
+
candle.volume;

});


this.series.setData(

Object.entries(distribution)
.map(
([price,volume])=>({

time:
Number(price) as any,

value:
volume

})
)

);

}


detach(){

if(
this.series &&
this.chart
){

safeRemoveSeries(
this.chart,
this.series

);

}

}

}
