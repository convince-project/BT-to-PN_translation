let sliderValue = 50;
let sliderX = 1075;
let sliderY = 80;
let sliderWidth = 200;
let sliderHeight = 20;
let slidermin = 30;
let slidermax = 1000;
let minzoom = 0.3;
let buttonImage;
let timing=(slidermax-slidermin)*sliderValue/100;

let Mode=0;


let startX, startY;
let isDragging = false;

function mousePressed() {
  
  // Check if mouse is over the button
  
  
  startX = (mouseX - 500) / zoom + 1000 / 2 - offsetX;
  startY = (mouseY - height / 2) / zoom + height / 2 - offsetY;
  isDragging = true;
  for (let k in shownPlaces){
    if(shownPlaces[k].isClicked(startX,startY)){
    }
  }
  for (let k in Transitions){
    
  }
  for (let k in Arcs){
    
  }
  
    if (
        mouseX > Buttons[1].buttonX &&
        mouseX < Buttons[1].buttonX + Buttons[1].buttonWidth &&
        mouseY > Buttons[1].buttonY &&
        mouseY < Buttons[1].buttonY + Buttons[1].buttonHeight
      ) {
        
        Buttons[1].buttonPress();
        for(let j=2;j<Buttons.length;j++){
          if(Buttons[j]!=Buttons[1] && (Buttons[1].buttonPressed) ){
            Buttons[j].buttonPressed=false;
          }
        }
      }
      
    if (
        mouseX > Buttons[0].buttonX &&
        mouseX < Buttons[0].buttonX + Buttons[0].buttonWidth &&
        mouseY > Buttons[0].buttonY &&
        mouseY < Buttons[0].buttonY + Buttons[0].buttonHeight
      ) {
        
        Buttons[0].buttonPress();
        for(let j=2;j<Buttons.length;j++){
          if(Buttons[j]!=Buttons[0] && (Buttons[0].buttonPressed) ){
            Buttons[j].buttonPressed=false;
          }
        }
        
      }
  
    if(Mbutton.buttonPressed==0){
      
      for(let i=2;i<6;i++){
        if (
          mouseX > Buttons[i].buttonX &&
          mouseX < Buttons[i].buttonX + Buttons[i].buttonWidth &&
          mouseY > Buttons[i].buttonY &&
          mouseY < Buttons[i].buttonY + Buttons[i].buttonHeight
        ) {
          
          Buttons[i].buttonPress();
          
          for(let j=2;j<Buttons.length;j++){
            if(Buttons[j]!=Buttons[i] && (Buttons[i].buttonPressed) ){
              Buttons[j].buttonPressed=false;
            }
          }
        }
      }
    }else{
      
      for(let i=6;i<Buttons.length;i++){
        if (
          mouseX > Buttons[i].buttonX &&
          mouseX < Buttons[i].buttonX + Buttons[i].buttonWidth &&
          mouseY > Buttons[i].buttonY &&
          mouseY < Buttons[i].buttonY + Buttons[i].buttonHeight
        ) {
          
          Buttons[i].buttonPress();
          for(let j=6;j<Buttons.length;j++){
            if(Buttons[j]!=Buttons[i] && (Buttons[i].buttonPressed) ){
              Buttons[j].buttonPressed=false;
            }
          }
          
        }
      }
  }

  
}

function mouseDragged() {
  // Check if mouse is over the slider handle
  if(Mbutton.buttonPressed==0){
    let sliderHandleX = map(sliderValue, 0, 100, sliderX, sliderX + sliderWidth - 20);
    if (
      mouseX > sliderHandleX - 50 &&
      mouseX < sliderHandleX + 50 &&
      mouseY > sliderY &&
      mouseY < sliderY + sliderHeight
    ) {
      // Update slider value based on mouse position
      sliderValue = map(
        constrain(mouseX, sliderX, sliderX + sliderWidth - 20),
        sliderX,
        sliderX + sliderWidth - 20,
        0,
        100
      );
      clearInterval(intervalID); // Clear the existing interval
      timing=int(sliderValue) * (slidermax - slidermin) / 100 + slidermin;
      // Set a new interval with updated delay
      intervalID = setInterval(Update,timing);
    }
  }else{
    
  }
  if (mouseX > 0 && mouseX < 1000 && mouseY > 0 && mouseY < height) {
    if (isDragging) {
      offsetX = mouseX - startX;
      offsetY = mouseY - startY;
      offsetX = (mouseX - 500) / zoom + 1000 / 2 - startX;
      offsetY = (mouseY - height / 2) / zoom + height / 2 - startY;
    }
  }
}

function mouseWheel(event) {
  if (mouseX > 0 && mouseX < 1000 && mouseY > 0 && mouseY < height) {
    let e=event.delta;
    if (e > 0) {
      zoomOut();
    } else {
      zoomIn();
    }
  
  }
}

function zoomIn() {
  let mx = mouseX - 1000 / 2;
  let my = mouseY - height / 2;
  offsetX -= mx * (1.0 / zoom - 1.0 / (zoom + zoomIncrement));
  offsetY -= my * (1.0 / zoom - 1.0 / (zoom + zoomIncrement));
  zoom += min(10, zoomIncrement);
}

function zoomOut() {
  if (zoom > minzoom) {
    let mx = mouseX - width / 2;
    let my = mouseY - height / 2;
    offsetX += mx * (1.0 / zoom - 1.0 / (zoom - zoomIncrement));
    offsetY += my * (1.0 / zoom - 1.0 / (zoom - zoomIncrement));
    zoom = max(minzoom, zoom - zoomIncrement);
  }
}

function draw_GUI() {
  // Draw slider
  fill(225);
  rect(width-300,0,width-2,height);
  line(width,0,width,height);
  Mbutton.drawButton();
  Cbutton.drawButton();
  if(Mbutton.buttonPressed==0){
    //rect(width/2, 10, width/2+20, height/2);
    fill(200);
    rect(sliderX, sliderY, sliderWidth, sliderHeight);
  
    // Draw slider handle
    fill(150);
    let sliderHandleX = map(sliderValue, 0, 100, sliderX, sliderX + sliderWidth - 20);
    rect(sliderHandleX, sliderY, 20, sliderHeight);
  
    
    for(let i=2;i<6;i++){
      Buttons[i].drawButton();
    }
  
    // Display slider value
    fill(0);
    textSize(16);
    textAlign(CENTER, CENTER);
    text("Speed: ", sliderX - 35, sliderY + sliderHeight / 2);
    text(
      "Value: " + (timing),
      sliderX + sliderWidth / 2,
      sliderY + sliderHeight + 20
    );
  }else{
    for(let i=6;i<Buttons.length;i++){
      Buttons[i].drawButton();
    }
    editor.drawEditor();
  }
}
