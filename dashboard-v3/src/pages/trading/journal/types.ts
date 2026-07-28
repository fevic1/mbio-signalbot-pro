export interface TradeRecord {

symbol:string;

direction:string;

setup:string;

confidence:number;

entry?:number;

exit?:number;

result?:
"WIN" |
"LOSS" |
"PENDING";

timestamp:number;

}
