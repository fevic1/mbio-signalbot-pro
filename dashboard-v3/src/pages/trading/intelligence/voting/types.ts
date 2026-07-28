export type AgentVote =
"LONG" |
"SHORT" |
"NO_TRADE";


export interface AgentDecision {

agent:string;

vote:AgentVote;

confidence:number;

reason:string;

}
