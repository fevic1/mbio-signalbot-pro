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


export class InitialBalanceOverlay implements ChartOverlay {

  private highSeries?: ISeriesApi<"Line">;
  private lowSeries?: ISeriesApi<"Line">;
  private chart?: IChartApi;


  constructor(
    private candles:Candle[]
  ){}


  attach(chart:IChartApi){

    this.chart = chart;


    this.highSeries =
      chart.addSeries(
        LineSeries,
        {
          lineWidth:1
        }
      );


    this.lowSeries =
      chart.addSeries(
        LineSeries,
        {
          lineWidth:1
        }
      );


    this.render();

  }


  update(
    candles:Candle[]
  ){

    this.candles = candles;

    this.render();

  }


  private render(){

    if(
      !this.highSeries ||
      !this.lowSeries
    ){
      return;
    }


    if(
      this.candles.length===0
    ){
      return;
    }


    const initial =
      this.candles.slice(0,30);


    const high =
      Math.max(
        ...initial.map(
          x=>x.high
        )
      );


    const low =
      Math.min(
        ...initial.map(
          x=>x.low
        )
      );


    this.highSeries.setData([
      {
        time:this.candles[0].time as any,
        value:high
      },
      {
        time:this.candles[
          this.candles.length-1
        ].time as any,
        value:high
      }
    ]);


    this.lowSeries.setData([
      {
        time:this.candles[0].time as any,
        value:low
      },
      {
        time:this.candles[
          this.candles.length-1
        ].time as any,
        value:low
      }
    ]);

  }


  detach(){

    if(
      this.highSeries &&
      this.chart
    ){
      safeRemoveSeries(
this.chart,
this.highSeries
      
);
    }


    if(
      this.lowSeries &&
      this.chart
    ){
      safeRemoveSeries(
this.chart,
this.lowSeries
      
);
    }

  }

}
