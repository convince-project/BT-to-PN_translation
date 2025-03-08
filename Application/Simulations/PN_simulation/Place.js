let place_radius = 30;

class Place {

  
  constructor(json) {
    this.name = new Name(json.getJSONObject("name"));
    this.id = json.getString("id");
    this.position = new Position(json.getJSONArray("position"));
    let initialMarkingUnparsed = new InitialMarking(json.getJSONObject("initialMarking"));
    this.initialmarking=new Map();
    this.tokens=new Map();
    this.inputs = [];
    this.outputs = [];
    let splitted=splitTokens(initialMarkingUnparsed.getValue(),",");
    if(splitted.length<2){
      this.initialmarking.set(Tokenslist[0],int(splitted));
      this.tokens.set(Tokenslist[0],int(splitted));
    }else{
      for(let i =0;i<splitted.length;i++){
        this.initialmarking.set(splitted[i],int(splitted[i+1]));
        this.tokens.set(splitted[i],int(splitted[i+1]));
        i++;
      }
    }
    this.capacity = json.getFloat("capacity");
  }
  

  isClicked(mouse_x,mouse_y){
    if((mouse_x-this.position.x)*(mouse_x-this.position.x)+(mouse_y-this.position.y)*(mouse_y-this.position.y)<place_radius*place_radius){
      console.log(this.id);
    }
    return true;
  }

  AddArc(arc, io) {
    if (io === "input") {
      append(this.inputs, arc);
    } else {
      append(this.outputs, arc);
    }
  }
  
  update(){
    // First find the enabled transition with highest priority
    let tempArray=[];
    let maxpriority=0;
    // This find the maximum priority of the enabled transitions
    for(let i=0;i<this.outputs.length;i++){
      if(this.outputs[i].status==1 && Transitions[this.outputs[i].target].status==1){
        if(maxpriority<Transitions[this.outputs[i].target].priority){
          maxpriority=Transitions[this.outputs[i].target].priority;
        }
      }
    }
    if(maxpriority>0){
      // Compile the list of enabled transitions
      let enabledTransitions=[];
      for(let i=0;i<this.outputs.length;i++){
        if(this.outputs[i].status==1 && Transitions[this.outputs[i].target].status==1 && Transitions[this.outputs[i].target].priority==maxpriority){
          append(enabledTransitions,this.outputs[i]);
        }
      }
      let selected=floor(random(enabledTransitions.length));
      enabledTransitions[selected].status=2;
    }
  }
  
  // Getter methods
  getName() {
    return this.name;
  }

  getId() {
    return this.id;
  }

  getToken() {
    return this.tokens;
  }

  setToken(Tokens, io) {
    if (io == 1) { // Input
      this.tokens += Tokens;
    } else { // Output
      this.tokens -= Tokens;
    }
  }

  getPosition() {
    return this.position;
  }

  getInitialMarking() {
    return this.initialMarking;
  }

  getCapacity() {
    return this.capacity;
  }

  show() {
    // Accessing the properties of the place object
    console.log("Name: " + this.getName().getValue());
    console.log("ID: " + this.getId());
    console.log("Position: " + this.getPosition().getX() + ", " + this.getPosition().getY());
    console.log("Initial Marking Value: " + this.getInitialMarking().getValue());
    console.log("Capacity: " + this.getCapacity());
  }

  paint() {
    // Example usage:
    this.name.nameDraw(round(this.getPosition().getX()),
      round(this.getPosition().getY() - 30));
    ellipse(round(this.getPosition().getX()), round(this.getPosition().getY()), place_radius, place_radius);
    stroke(0);
    fill(0);
    paintMarking(this.tokens,this.getPosition().getX(),this.getPosition().getY());
  }
  
  
}

Place.prototype.name="";
Place.prototype.id="";
Place.prototype.position={};
Place.prototype.initialmarking=new Map();
Place.prototype.tokens=new Map();
Place.prototype.inputs = [];
Place.prototype.outputs = [];
Place.prototype.capacity=0;

class Name {
  constructor(json) {
    this.offset = json.getJSONArray("offset");
    this.value = json.getString("value");
  }

  // Getter methods
  getOffset() {
    return this.offset;
  }

  getValue() {
    return this.value;
  }

  nameDraw(x, y) {
    fill(0,0,255);
    
    textSize(12/(sqrt(zoom)));
    
    text(this.value,float(x) + float(this.offset.data[0]), float(y) + float(this.offset.data[1]));

    fill(255);
  }
}

class Position {
  constructor(json) {
    this.x = float(json.data[0]);
    this.y = float(json.data[1]);
  }

  // Getter methods
  getX() {
    return this.x;
  }

  getY() {
    return this.y;
  }
}

class InitialMarking {
  constructor(json) {
    this.offset = json.getJSONArray("offset");
    this.value = json.getString("value");
  }

  // Getter methods
  getOffset() {
    return this.offset;
  }

  getValue() {
    return this.value;
  }
}
