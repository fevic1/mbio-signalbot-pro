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


export class ValueAreaOverlay implements ChartOverlay {

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
      !this.lowSeries ||
      this.candles.length===0
    ){
      return;
    }


    const distribution:
      Record<string,number> = {};


    let totalVolume = 0;


    this.candles.forEach(
      candle=>{

        const price =
          (
            candle.high +
            candle.low +
            candle.close
          ) / 3;


        const key =
          price.toFixed(2);


        distribution[key] =
          (
            distribution[key] ?? 0
          )
          +
          candle.volume;


        totalVolume += candle.volume;

      }
    );


    const levels =
      Object.entries(distribution)
      .sort(
        ([a],[b]) =>
          Number(a)-Number(b)
      );


    let accumulated = 0;

    let min = Number(levels[0][0]);
    let max = Number(levels[0][0]);


    const target =
      totalVolume * 0.7;


    const pocIndex =
      levels
      .map(x=>x[1])
      .indexOf(
        Math.max(
          ...levels.map(x=>x[1])
        )
      );


    for(
      let i=pocIndex;
      i<levels.length &&
      accumulated<target;
      i++
    ){

      accumulated += levels[i][1];

      max =
        Number(levels[i][0]);

    }


    for(
      let i=pocIndex-1;
      i>=0 &&
      accumulated<target;
      i--
    ){

      accumulated += levels[i][1];

      min =
        Number(levels[i][0]);

    }


    const start =
      this.candles[0].time as any;

    const end =
      this.candles[
        this.candles.length-1
      ].time as any;


    this.highSeries.setData([
      {
        time:start,
        value:max
      },
      {
        time:end,
        value:max
      }
    ]);


    this.lowSeries.setData([
      {
        time:start,
        value:min
      },
      {
        time:end,
        value:min
      }
    ]);

  }


  detach(){

    if(
      this.chart &&
      this.highSeries
    ){
      safeRemoveSeries(
this.chart,
this.highSeries
      
);
    }


    if(
      this.chart &&
      this.lowSeries
    ){
      safeRemoveSeries(
this.chart,
this.lowSeries
      
);
    }

  }

}
