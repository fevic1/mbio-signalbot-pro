export interface StrategyTask {

name:string;

interval:number;

}


export class StrategyScheduler {


private tasks:StrategyTask[]=[];


register(
task:StrategyTask
){

this.tasks.push(task);

}


getTasks(){

return this.tasks;

}


}
