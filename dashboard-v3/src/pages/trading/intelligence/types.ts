export type SignalDirection =
"LONG" | "SHORT";


export interface TradeSetup {

symbol:string;

direction:SignalDirection;

setup:string;

confidence:number;

reasons:string[];

timestamp:number;

}
