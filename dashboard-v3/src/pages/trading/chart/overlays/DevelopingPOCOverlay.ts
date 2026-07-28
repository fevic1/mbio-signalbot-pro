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


export class DevelopingPOCOverlay implements ChartOverlay {

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


const data:any[]=[];


for(
let i=1;
i<=this.candles.length;
i++
){

const slice =
this.candles.slice(0,i);


const volumeMap:
Record<string,number>={};


slice.forEach(c=>{

const price =
(
c.high+c.low+c.close
)/3;


const key =
price.toFixed(2);


volumeMap[key]=
(volumeMap[key]??0)
+c.volume;

});


const poc =
Object.entries(volumeMap)
.sort(
(a,b)=>b[1]-a[1]
)[0];


if(poc){

data.push({

time:
this.candles[i-1].time as any,

value:
Number(poc[0])

});

}

}


this.series.setData(data);

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
