let Pbutton;
let Sbutton;
let Rbutton;
let Resbutton;
let Mbutton;
let Cbutton;
let placebutton,transitionbutton,arcbutton,interfacebutton;
let Buttons=[];
let buttonWidth=60;
let buttonHeight=40;

class Stepbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1084;
    this.buttonY = 150;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
  }

  drawButton() {
    // Draw button
    fill(this.buttonPressed ? color(0, 255, 0) : color(150));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    push();
    let x2 = this.buttonX + this.buttonWidth / 2 + arc_trianglesize - 2;
    let y2 = this.buttonY + this.buttonHeight / 2;
    
    let angle = 0;
    let arrowX1 = this.buttonsize * cos(angle - PI / 6);
    let arrowY1 = this.buttonsize * sin(angle - PI / 6);
    let arrowX2 = this.buttonsize * cos(angle + PI / 6);
    let arrowY2 = this.buttonsize * sin(angle + PI / 6);
    translate(x2, y2);

    fill(0);
    triangle(0, 0, -arrowX1, -arrowY1, -arrowX2, -arrowY2);
    rect(0, -10, 2, 20);
    fill(255);
    pop();
  }

  buttonPress() {
    this.buttonPressed = !this.buttonPressed;
    this.drawButton();
    Update();
    this.buttonPressed = !this.buttonPressed;
  }
}

class Playbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1012;
    this.buttonY = 150;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 + arc_trianglesize;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    this.arrowX1 = this.buttonsize * cos(angle - PI / 6);
    this.arrowY1 = this.buttonsize * sin(angle - PI / 6);
    this.arrowX2 = this.buttonsize * cos(angle + PI / 6);
    this.arrowY2 = this.buttonsize * sin(angle + PI / 6);
  }

  drawButton() {
    // Draw button
    fill(!this.buttonPressed ? color(0, 255, 0) : color(255,0,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    if(!this.buttonPressed){
      push();
      translate(this.x2, this.y2);
      fill(0);
      triangle(0, 0, -this.arrowX1, -this.arrowY1, -this.arrowX2, -this.arrowY2);
      pop();
    }else{
      push();
      fill(0);
        translate(this.x2, this.y2);
        rect(-this.buttonsize,-this.buttonsize/2,this.buttonsize,this.buttonsize);
      pop();
    }
    
    fill(255);
    
  }

  buttonPress() {
    this.buttonPressed= !this.buttonPressed;
  }
}


class Recordbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1156;
    this.buttonY = 150;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(255,0,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    translate(this.x2, this.y2);
    fill(0);
    ellipse(0, 0, this.buttonsize,this.buttonsize);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
    this.buttonPressed= !this.buttonPressed;
    if(this.buttonPressed){
      gif = new GIF({
        workers: 2,
        quality: 10,
      });
    }else{
      gif.render();
      gif.on('finished', function(blob) {
        saveAs(blob, 'output.gif');
      });
      
      
    }
    
    
  }
}

class Resetbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1228;
    this.buttonY = 150;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(255,0,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    translate(this.x2, this.y2);
    noFill();
    strokeWeight(5);
    rotate(PI/2+PI/3);
    arc(0, 0, this.buttonsize,this.buttonsize,PI, 5*PI/2);
    translate(-5,8);
    let angle = PI+PI/12;
    let arrowX1 =  - 5 * cos(angle - PI / 6);
    let arrowY1 =  - 5 * sin(angle - PI / 6);
    let arrowX2 =  - 5 * cos(angle + PI / 6);
    let arrowY2 = - 5 * sin(angle + PI / 6);
    // Draw arrowhead (triangle)
    triangle(0, 0, arrowX1, arrowY1, arrowX2, arrowY2);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
     
    this.buttonPressed = !this.buttonPressed;
   
    this.drawButton();
     for(let p in Places){
       for(let i =0;i<Tokenslist.length;i++){
         Places[p].tokens.set(Tokenslist[i],int(Places[p].initialmarking.get(Tokenslist[i])));
       }
     }
     
     for(let p in Arcs){
       Arcs[p].status=0;
     }
     
     for(let p in Transitions){
       Transitions[p].status=0;
     }
     Update();
    this.buttonPressed = !this.buttonPressed;
    
  }
    
    
  
}

class Clearbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1110;
    this.buttonY = 10;
    this.buttonWidth = 80;
    this.buttonHeight = 40;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(255,0,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    translate(this.x2, this.y2);
    fill(0);
    text("Clear", 0,0);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
     
    this.buttonPressed = !this.buttonPressed;
    Places=[];
    Transitions=[];
    Arcs=[];
    translate(-offsetX, -offsetY);
    scale(1/zoom);
    zoom=1.0;
    offsetX=0.0;
    offsetY=0.0;
    this.buttonPressed = !this.buttonPressed;
 }
    
    
  
}


class Modebutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1010;
    this.buttonY = 10;
    this.buttonWidth = 80;
    this.buttonHeight = 40;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(0, 255, 0) : color(255,0,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    push();
    
    translate(this.x2, this.y2);
    fill(0);
    if(this.buttonPressed){
      text("Simulate", 0,0);
    }else{
      text("Edit", 0,0);
    }
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
    this.buttonPressed= !this.buttonPressed;
    
    
  }
}


class Placebutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1012;
    this.buttonY = 80;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(0,255,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    
    translate(this.x2, this.y2);
    fill(255);
    ellipse(0,0,place_radius,place_radius);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
    this.buttonPressed= !this.buttonPressed;
    
    
  }
}

class Transitionbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1084;
    this.buttonY = 80;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    let angle = 0;
    this.status=0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(0,255,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    
    translate(this.x2, this.y2);
    
    
    fill(0);
    
    rect(-transition_width/2,-transition_height/2,
         +transition_width,+transition_height);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
    
      this.buttonPressed=!this.buttonPressed;
    
    
  }
}

class Arcbutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1156;
    this.buttonY = 80;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    this.status=0;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(0,255,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    
    push();
    translate(this.x2-10,this.y2);
    fill(0);
    line(0,0,20,0);
    let angle = 0;
    let arrowX1 = 20 - arc_trianglesize * cos(angle - PI / 6);
    let arrowY1 =  - arc_trianglesize * sin(angle - PI / 6);
    let arrowX2 = 20 - arc_trianglesize * cos(angle + PI / 6);
    let arrowY2 = - arc_trianglesize * sin(angle + PI / 6);
    // Draw arrowhead (triangle)
    triangle(20, 0, arrowX1, arrowY1, arrowX2, arrowY2);
    pop();
    
    
    fill(255);
    
    
      
  }

  buttonPress() {
        
      this.buttonPressed= !this.buttonPressed;
      
  }
}

class Interfacebutton {
  constructor() {
    this.buttonsize = 20;
    this.buttonX = 1228;
    this.buttonY = 80;
    this.buttonWidth = buttonWidth;
    this.buttonHeight = buttonHeight;
    this.buttonPressed = false;
    this.status=0;
    let angle = 0;
    this.x2 = this.buttonX + this.buttonWidth / 2 ;
    this.y2 = this.buttonY + this.buttonHeight / 2;
    
  }

  drawButton() {
    
    // Draw button
    fill(!this.buttonPressed ? color(125, 125, 125) : color(0,255,0));
    rect(this.buttonX, this.buttonY, this.buttonWidth, this.buttonHeight);
    
    
    fill(255);
    rect(this.x2-transition_height/2,this.y2-transition_height/2,transition_height,transition_height);    
    
    fill(255);
    
    
      
  }

  buttonPress() {
        
      this.buttonPressed= !this.buttonPressed;
      
  }
}
