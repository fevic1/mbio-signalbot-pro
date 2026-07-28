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


export class LiquiditySweepOverlay implements ChartOverlay {


private series?:ISeriesApi<"Line">;



constructor(
private candles:Candle[]
){}


attach(chart:IChartApi){


this.series =
chart.addSeries(
LineSeries
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


const sweeps:any[]=[];


for(
let i=2;
i<this.candles.length;
i++
){

const a=this.candles[i-2];
const b=this.candles[i];


if(
b.high>a.high &&
b.close<a.high
){

sweeps.push({

time:b.time as any,

value:b.high

});

}

}


this.series.setData(
sweeps
);

}


detach(){}

}
