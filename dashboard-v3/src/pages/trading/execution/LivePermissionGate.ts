export class LivePermissionGate {


private enabled=false;


enable(){

this.enabled=true;

}


disable(){

this.enabled=false;

}


canTrade(){

return this.enabled;

}


}
