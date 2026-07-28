export interface MemoryEvent {

pattern:string;

result:
"WIN" |
"LOSS";

}


export class MemoryFeedbackLoop {


private memory:MemoryEvent[]=[];


record(
event:MemoryEvent
){

this.memory.push(
event
);

}


getMemory(){

return this.memory;

}


}
