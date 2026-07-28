import { safeRemoveSeries } from "./safeRemoveSeries";
import {
  IChartApi,
  ISeriesApi,
  LineSeries,
} from "lightweight-charts";

import {
  Candle
} from "../../market/state/marketStore";

import {
  ChartOverlay
} from "./OverlayBridge";


export class FVGOverlay implements ChartOverlay {

private series?:ISeriesApi<"Line">;

private chart?:IChartApi;


constructor(
private candles:Candle[]
){}


attach(chart:IChartApi){

this.chart=chart;

this.series =
chart.addSeries(
LineSeries,
{
lineWidth:1
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


const gaps:any[]=[];


for(
let i=2;
i<this.candles.length;
i++
){

const a=this.candles[i-2];
const c=this.candles[i];


if(a.high < c.low){

gaps.push({

time:c.time as any,

value:
(a.high+c.low)/2

});

}


if(a.low > c.high){

gaps.push({

time:c.time as any,

value:
(a.low+c.high)/2

});

}

}


this.series.setData(
gaps
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
