import { IChartApi, ISeriesApi } from "lightweight-charts";

const removedSeries = new WeakSet<object>();

export function safeRemoveSeries(
  chart: IChartApi | null | undefined,
  series: ISeriesApi<any> | null | undefined
){

  if(!chart || !series){
    return;
  }

  if(removedSeries.has(series)){
    return;
  }

  try{

    chart.removeSeries(series);

    removedSeries.add(series);

  }catch(error){

    console.warn(
      "safeRemoveSeries ignored",
      error
    );

  }

}
