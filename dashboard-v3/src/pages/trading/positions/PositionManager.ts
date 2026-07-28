export interface Position {

symbol:string;

size:number;

entry:number;

side:
"LONG" |
"SHORT";

}


export class PositionManager {


private positions:
Position[]=[];


add(
position:Position
){

this.positions.push(
position
);

}


getPositions(){

return this.positions;

}


clear(){

this.positions=[];

}


}
