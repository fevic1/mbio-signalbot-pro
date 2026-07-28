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


export class EqualLevelsOverlay implements ChartOverlay {

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


const levels:any[]=[];


for(
let i=2;
i<this.candles.length;
i++
){

const a=this.candles[i-2];
const b=this.candles[i];


const highDiff =
Math.abs(
a.high-b.high
);


const lowDiff =
Math.abs(
a.low-b.low
);


if(
highDiff <
a.high*0.001
){

levels.push({

time:b.time as any,

value:
(a.high+b.high)/2

});

}


if(
lowDiff <
a.low*0.001
){

levels.push({

time:b.time as any,

value:
(a.low+b.low)/2

});

}

}


this.series.setData(levels);

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
