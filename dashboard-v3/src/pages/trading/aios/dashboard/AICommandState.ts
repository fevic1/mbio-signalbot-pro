export interface AIStatus {

agent:string;

status:
"ACTIVE" |
"IDLE" |
"ERROR";

message:string;

}


export const defaultAgents:AIStatus[]=[

{
agent:"Research",
status:"ACTIVE",
message:"Scanning markets"
},

{
agent:"Risk",
status:"ACTIVE",
message:"Monitoring exposure"
},

{
agent:"Execution",
status:"IDLE",
message:"Waiting"
}

];
