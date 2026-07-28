import {
TradeSetup
} from "../types";


import {
technicalAgent,
skepticAgent,
riskAgent
} from "./agents";


import {
calculateConsensus
} from "./ConsensusEngine";


import {
AgentDecision
} from "./types";


export function runVoting(
setup:TradeSetup
){

const decisions:AgentDecision[]=[

technicalAgent(setup),

skepticAgent(setup),

riskAgent(setup)

];


const consensus =
calculateConsensus(
decisions
);


return {

decisions,

consensus

};

}
