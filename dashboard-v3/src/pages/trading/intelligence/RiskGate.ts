export interface RiskRequest {

confidence:number;

riskPercent:number;

}


export function validateRisk(
request:RiskRequest
){

if(
request.riskPercent > 1
){

return {

approved:false,

reason:
"Risk exceeds maximum"

};

}


if(
request.confidence < 70
){

return {

approved:false,

reason:
"Insufficient confidence"

};

}


return {

approved:true,

reason:
"Risk accepted"

};

}
