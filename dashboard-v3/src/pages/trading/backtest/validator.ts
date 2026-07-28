export interface BacktestResult {

winRate:number;

profitFactor:number;

trades:number;

}


export function validateStrategy(
result:BacktestResult
){

return {

approved:

result.winRate >=50 &&
result.profitFactor >=1.2 &&
result.trades >=100,


result

};

}
