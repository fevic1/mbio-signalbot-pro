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


export class MitigationBlockOverlay implements ChartOverlay {


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


const zones:any[]=[];


for(
let i=1;
i<this.candles.length;
i++
){

const previous =
this.candles[i-1];

const current =
this.candles[i];


if(
current.low <= previous.close &&
current.close > previous.high
){

zones.push({

time:current.time as any,

value:previous.close

});

}


if(
current.high >= previous.close &&
current.close < previous.low
){

zones.push({

time:current.time as any,

value:previous.close

});

}

}


this.series.setData(zones);

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
