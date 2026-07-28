export function calculatePositionSize(
capital:number,
riskPercent:number,
stopDistance:number
){

const risk =
capital *
(riskPercent/100);


return risk / stopDistance;

}
