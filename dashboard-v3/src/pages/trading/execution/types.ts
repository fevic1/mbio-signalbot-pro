export type OrderSide =
"BUY" |
"SELL";


export type OrderType =
"MARKET" |
"LIMIT";


export interface OrderRequest {

symbol:string;

side:OrderSide;

type:OrderType;

quantity:number;

price?:number;

}


export interface OrderResult {

success:boolean;

orderId?:string;

message:string;

}
