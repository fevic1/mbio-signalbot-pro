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


export class POCOverlay implements ChartOverlay {

  private series?: ISeriesApi<"Line">;

  private chart?: IChartApi;


  constructor(
    private candles:Candle[]
  ){}


  attach(chart:IChartApi){

    this.chart = chart;


    this.series =
      chart.addSeries(
        LineSeries,
        {
          lineWidth:2
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
      !this.series ||
      this.candles.length===0
    ){
      return;
    }


    const volumeByPrice:
      Record<string,number> = {};


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


        volumeByPrice[key] =
          (
            volumeByPrice[key] ?? 0
          )
          +
          candle.volume;

      }
    );


    const poc =
      Object.entries(
        volumeByPrice
      )
      .sort(
        (
          [,a],
          [,b]
        )=>b-a
      )[0];


    if(!poc){
      return;
    }


    const price =
      Number(poc[0]);


    this.series.setData([

      {
        time:
          this.candles[0].time as any,

        value:price
      },

      {
        time:
          this.candles[
            this.candles.length-1
          ].time as any,

        value:price
      }

    ]);

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


    this.series = undefined;
    this.chart = undefined;

  }

}
