let transition_width = 10;
let transition_height = 30;

class Transition {
  constructor(json) {
    this.orientation = json.getFloat("orientation");
    this.timed = json.getString("timed");
    this.rate = json.getFloat("rate");
    this.name = new Name(json.getJSONObject("name"));
    this.infiniteServer = json.getString("infiniteServer");
    this.id = json.getString("id");
    this.position = new Position(json.getJSONArray("position"));
    this.priority = int(json.getFloat("priority"));
    this.inputs = [];
    this.outputs = [];
    this.status = 0;
  }

  // Getter methods
  getOrientation() {
    return this.orientation;
  }

  isTimed() {
    return this.timed;
  }

  getRate() {
    return this.rate;
  }

  getName() {
    return this.name;
  }

  isInfiniteServer() {
    return this.infiniteServer;
  }

  AddArc(arc, io) {
    if (io === "input") {
      append(this.inputs, arc);
    } else {
      append(this.outputs, arc);
    }
  }

  getId() {
    return this.id;
  }

  getPosition() {
    return this.position;
  }

  getPriority() {
    return this.priority;
  }

  show() {
    // Example usage:

    // Accessing the properties of the transition object
    console.log("Orientation: " + this.getOrientation());
    console.log("Timed: " + this.isTimed());
    console.log("Rate: " + this.getRate());
    console.log("Name: " + this.getName().getValue());
    console.log("Infinite Server: " + this.isInfiniteServer());
    console.log("ID: " + this.getId());
    console.log("Position: " + this.getPosition().getX() + ", " + this.getPosition().getY());
    console.log("Priority: " + this.getPriority());
  }

  update(){
    if(this.status==0){ // If the transition is not enabled
    
      // Check if it should be enabled depending on the inputs
      let counter = 0;
      for(let i=0;i<this.inputs.length;i++){
        if(Arcs[this.inputs[i].id].status==1){
          counter++;
        }
      }
      // Enable it
      if(counter==this.inputs.length){
        this.status=1;
        
      }else{
        this.status=0;
      }
      
    }else if(this.status==1){ // If enable start the logic to see if it should fire
      let counter=0
      for(let i=0;i<this.inputs.length;i++){
          if(this.inputs[i].status==2){
            counter++;
          }
        }
        // fire it
      if(counter==this.inputs.length){
        this.status=2;
      }else{
        this.status=0;
      }
      
      
    }else{ // if it has fired reset it to non active
      this.status=0;
      
      for(let i =0;i<this.inputs.length;i++){
        for(let j=0;j<Tokenslist.length;j++){
          Places[this.inputs[i].source].tokens.set(Tokenslist[j],
          int(Places[this.inputs[i].source].tokens.get(Tokenslist[j]))-int(this.inputs[i].inscription.get(Tokenslist[j])));
        }
      }
      for(let i =0;i<this.outputs.length;i++){
        for(let j=0;j<Tokenslist.length;j++){
          // print("Output",this.outputs[i], Places[this.outputs[i].target].tokens.get(Tokenslist[j]),this.outputs[i].inscription.get(Tokenslist[i]));
          Places[this.outputs[i].target].tokens.set(Tokenslist[j],
          int(Places[this.outputs[i].target].tokens.get(Tokenslist[j]))+int(this.outputs[i].inscription.get(Tokenslist[j])));
        }
      }
    }
  }

  paint() {
    // Example usage:

    this.name.nameDraw(round(this.getPosition().getX()),
      round(this.getPosition().getY()) - 10);
    if (this.timed === "true") {
      if (this.status === 0) {
        fill(255);
      } else if (this.status === 1) {
        fill(255, 0, 0);
      } else {
        fill(0, 255, 0);
      }
    } else {
      if (this.status === 0) {
        fill(0);
      } else if (this.status === 1) {
        fill(255, 0, 0);
      } else {
        fill(0, 255, 0);
      }
    }
    rect(
      round(this.getPosition().getX() - transition_width / 2),
      round(this.getPosition().getY() - transition_height / 2),
      transition_width,
      transition_height
    );
    fill(255);
  }
}


Transition.prototype.orientation = 0;
Transition.prototype.timed = 0;
Transition.prototype.rate = 0;
Transition.prototype.name = "";
Transition.prototype.infiniteServer = 0;
Transition.prototype.id = "";
Transition.prototype.position = {};
Transition.prototype.priority = 0;
Transition.prototype.inputs = [];
Transition.prototype.outputs = [];
Transition.prototype.status = 0;
