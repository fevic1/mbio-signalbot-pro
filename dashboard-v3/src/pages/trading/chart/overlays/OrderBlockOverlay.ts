import { safeRemoveSeries } from "./safeRemoveSeries";
import {
IChartApi,
ISeriesApi,
LineSeries
} from "lightweight-charts";

import {
Candle
} from "../../market/state/marketStore";

import {
ChartOverlay
} from "./OverlayBridge";


export class OrderBlockOverlay implements ChartOverlay {


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
lineWidth:2
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


const blocks:any[]=[];


for(
let i=1;
i<this.candles.length;
i++
){

const prev=this.candles[i-1];
const curr=this.candles[i];


if(
curr.close>curr.open &&
prev.close<prev.open &&
curr.close>prev.high
){

blocks.push({

time:curr.time as any,

value:
(prev.open+prev.close)/2

});

}

}


this.series.setData(
blocks
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
