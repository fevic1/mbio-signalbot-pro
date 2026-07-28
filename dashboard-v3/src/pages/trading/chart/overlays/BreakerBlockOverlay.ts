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


export class BreakerBlockOverlay implements ChartOverlay {

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
let i=2;
i<this.candles.length;
i++
){

const a=this.candles[i-2];
const b=this.candles[i];


if(
a.close<a.open &&
b.close>a.high
){

blocks.push({

time:b.time as any,

value:a.open

});

}


if(
a.close>a.open &&
b.close<a.low
){

blocks.push({

time:b.time as any,

value:a.open

});

}

}


this.series.setData(blocks);

}


detach(){

if(
this.chart &&
this.series
){

safeRemoveSeries(
this.chart,
this.series

);

}

}

}
