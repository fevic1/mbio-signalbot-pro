import {
AgentDecision
} from "./types";


export function calculateConsensus(
votes:AgentDecision[]
){

const valid =
votes.filter(
x=>x.vote!=="NO_TRADE"
);


if(valid.length===0){

return {

decision:"NO_TRADE",

confidence:0

};

}


const direction =
valid[0].vote;


const agreement =
valid.filter(
x=>x.vote===direction
).length;


return {

decision:direction,

confidence:
Math.round(
agreement /
votes.length *
100
)

};

}
