import { Candle } from "../state/marketStore";

export interface MarketDataAdapter {

  connect(
    symbol:string,
    callback:(candle:Candle)=>void
  ):void;

  disconnect():void;

}
