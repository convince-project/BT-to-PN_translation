class Editor{
  
  constructor(){
    
  }
  
  drawEditor(){
    fill(255);
    rect(1010,200,280,height-200-60);
    let tempPlace;
    if(Buttons[6].buttonPressed){
      print(Object.keys(Place.prototype));
    }else if(Buttons[7].buttonPressed){
      print(Object.keys(Transition.prototype));
    }else if(Buttons[8].buttonPressed){
      print(Object.keys(Arc.prototype));
    }else if(Buttons[9].buttonPressed){
      print(Object.keys(Place.prototype));
    }
  }
}
