export interface StrategyMemory {

pattern:string;

wins:number;

losses:number;

}


export function updateMemory(
memory:StrategyMemory,
win:boolean
){

return {

...memory,

wins:
memory.wins +
(win ? 1:0),

losses:
memory.losses +
(win ? 0:1)

};

}
