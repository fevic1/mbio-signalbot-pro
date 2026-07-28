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


export class VWAPOverlay implements ChartOverlay {

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


    this.series.setData(
      this.calculate()
    );

  }


  update(
    candles:Candle[]
  ){

    this.candles = candles;


    if(!this.series){
      return;
    }


    const data =
      this.calculate();


    const latest =
      data[data.length - 1];


    if(latest){

      this.series.update(
        latest
      );

    }

  }


  private calculate(){

    let volume = 0;
    let value = 0;


    return this.candles.map(
      candle=>{

        const price =
          (
            candle.high +
            candle.low +
            candle.close
          ) / 3;


        value +=
          price *
          candle.volume;


        volume +=
          candle.volume;


        return {

          time:candle.time as any,

          value:
            value /
            volume

        };

      }
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


    this.series = undefined;
    this.chart = undefined;

  }

}
