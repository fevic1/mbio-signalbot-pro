export interface ConfluenceInput {

vwap:boolean;

fvg:boolean;

orderBlock:boolean;

liquiditySweep:boolean;

marketProfile:boolean;

}


export function calculateConfluence(
input:ConfluenceInput
){

let score=0;


if(input.vwap)
score+=15;


if(input.fvg)
score+=20;


if(input.orderBlock)
score+=20;


if(input.liquiditySweep)
score+=25;


if(input.marketProfile)
score+=20;


return {

score,

grade:
score>=85
?
"High"
:
score>=70
?
"Valid"
:
score>=40
?
"Watch"
:
"Weak"

};

}
