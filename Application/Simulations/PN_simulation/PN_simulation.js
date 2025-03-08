let xml;
let infty = 1e32;
let maxX = -infty;
let maxY = -infty;
let minX = infty;
let minY = infty;

let screenX, screenY, screenW, screenH;

let zoom = 1.0;
let zoomIncrement = 0.1;
let offsetX = 0;
let offsetY = 0;

let Places;
let Transitions;
let Arcs;
let shownPlaces;
let shownTransitions;
let shownArcs;
let Tokens;
let Tokenslist;

let editor;

let width_c = 100;
let height_c = 100;

let valtag = ["priority", "rate", "probability", "capacity", "orientation"];
let booltag = ["tagged", "timed", "infiniteServer", "inscription"];
let floattags = ["x", "y"];

let gif;
let frameImage;

let fileInput;

// Function to handle file selection
function handleFile(file) {
  // Check if the file is not null
  if (file) {
    // Read the contents of the file
    let fileContent = file.data;
    xml=fileContent;
    // Display the content of the file
    preparation();
  } else {
  }
}

function setup() {
  let canvas=createCanvas(1300, 600);
  Tokens={};
  Places = {}; // Initialize the empty array of places
  Transitions = {}; // Initialize the empty array of transitions
  Arcs = {}; // Initialize the empty array of arcs
  // Create a file input
  fileInput = createFileInput(handleFile);
  fileInput.type = 'file';
  fileInput.accept = '.xml';
  // Set the position of the file input
  fileInput.position(10, canvas.position.y);
  // Your setup code here
  
  
  Mbutton = new Modebutton(); // Button 0
  append(Buttons,Mbutton);
  Cbutton = new Clearbutton(); // Button 1
  append(Buttons,Cbutton);
  
  Pbutton = new Playbutton(); // Button 2
  append(Buttons,Pbutton);
  Sbutton = new Stepbutton(); // Button 3
  append(Buttons,Sbutton);
  Rbutton = new Recordbutton(); // Button 4
  append(Buttons,Rbutton);
  Resbutton = new Resetbutton(); // Button 5
  append(Buttons,Resbutton);
  placebutton = new Placebutton(); // Button 6
  append(Buttons,placebutton);
  transitionbutton = new Transitionbutton(); // Button 7
  append(Buttons,transitionbutton);
  arcbutton = new Arcbutton(); // Button 8
  append(Buttons,arcbutton);
  interfacebutton = new Interfacebutton(); // Button 9
  append(Buttons,interfacebutton);
  
  editor=new Editor();
  
}

function draw() {
  background(255);
  fill(255);
  rect(0,0,width-1,height);
  push();
  screenX = 0;
  screenY = 0;
  translate(1000 / 2, height / 2);
  scale(zoom);

  translate(-1000 / 2, -height / 2);

  translate(offsetX, offsetY);
  
  screenX = (screenX - 500) / zoom + 1000 / 2 - offsetX;
  screenY = (screenY - height / 2) / zoom + height / 2 - offsetY;
  screenW = 1000 / zoom;
  screenH = height / zoom;
  
  shownPlaces=[];
  shownTransitions=[];
  shownArcs=[];
  
  for (let p in Arcs) {
    // print(Arcs[p].status,p);
    let circleX, circleY;
    let rectX, rectY;

    // Find intersection points

    if (Places.hasOwnProperty(Arcs[p].source)) {
      circleX = Places[Arcs[p].source].getPosition().x;
      circleY = Places[Arcs[p].source].getPosition().y;
      rectX = Transitions[Arcs[p].target].getPosition().x;
      rectY = Transitions[Arcs[p].target].getPosition().y;
    } else {
      circleX = Places[Arcs[p].target].getPosition().x;
      circleY = Places[Arcs[p].target].getPosition().y;
      rectX = Transitions[Arcs[p].source].getPosition().x;
      rectY = Transitions[Arcs[p].source].getPosition().y;
    }
   
    if (
      lineRectangleIntersect(
        circleX,
        circleY,
        rectX,
        rectY,
        screenX,
        screenY,
        screenW,
        screenH
      )
    ) {
      
      Arcs[p].paint();
      append(shownArcs,Arcs[p]);
    }
  }
  for (let p in Places) {
    if (
      circleRectangleIntersect(
        Places[p].getPosition().x,
        Places[p].getPosition().y,
        place_radius * zoom,
        screenX,
        screenY,
        screenW,
        screenH
      )
    ) {
      Places[p].paint();
      append(shownPlaces,Places[p]);
    }
  }
  for (let p in Transitions) {
    //Transitions[p].update();
    if (
      rectanglesIntersect(
        Transitions[p].getPosition().x,
        Transitions[p].getPosition().y,
        transition_width,
        transition_height,
        screenX,
        screenY,
        screenW,
        screenH
      )
    ) {
      Transitions[p].paint();
      append(shownTransitions,Transitions[p]);  
  }
  }
  pop();
  draw_GUI();
}

// Set interval to execute myFunction every 1000 milliseconds (1 second)
 let intervalID =setInterval(Update, timing);

function Update(){
  
  if(Sbutton.buttonPressed || Pbutton.buttonPressed || Rbutton.buttonPressed){
    for (let p in Arcs) {
      Arcs[p].update();
    }
    
    for (let p in Places) {
      Places[p].update();
    }
    for (let p in Transitions) {
      Transitions[p].update();
    }
  }
  if(Rbutton.buttonPressed){
    frameImage = get(0, 0, 1000, height);
    
    // Add the captured frame to the GIF
    gif.addFrame(frameImage.canvas, { delay: timing  });
  }
  
}

// Function to check intersection between a circle and a rectangle
function circleRectangleIntersect(
  circleX,
  circleY,
  circleRadius,
  rectX,
  rectY,
  rectWidth,
  rectHeight
) {
  return (
    circleX > rectX &&
    circleX < rectX + rectWidth &&
    circleY > rectY &&
    circleY < rectY + rectHeight
  );
}

// Function to check intersection between two rectangles
function rectanglesIntersect(
  rect1X,
  rect1Y,
  rect1Width,
  rect1Height,
  rect2X,
  rect2Y,
  rect2Width,
  rect2Height
) {
  return (
    rect1X < rect2X + rect2Width &&
    rect1X + rect1Width > rect2X &&
    rect1Y < rect2Y + rect2Height &&
    rect1Y + rect1Height > rect2Y
  );
}

// Function to check intersection between a line and a rectangle
function lineRectangleIntersect(
  x1,
  y1,
  x2,
  y2,
  rectX,
  rectY,
  rectWidth,
  rectHeight
) {
  // Check if either end point is inside the rectangle
  if (
    pointInRectangle(x1, y1, rectX, rectY, rectWidth, rectHeight) ||
    pointInRectangle(x2, y2, rectX, rectY, rectWidth, rectHeight)
  ) {
    return true;
  }

  // Check for intersection with each side of the rectangle
  return (
    lineIntersect(x1, y1, x2, y2, rectX, rectY, rectX + rectWidth, rectY) ||
    lineIntersect(x1, y1, x2, y2, rectX, rectY, rectX, rectY + rectHeight) ||
    lineIntersect(
      x1,
      y1,
      x2,
      y2,
      rectX + rectWidth,
      rectY,
      rectX + rectWidth,
      rectY + rectHeight
    ) ||
    lineIntersect(
      x1,
      y1,
      x2,
      y2,
      rectX,
      rectY + rectHeight,
      rectX + rectWidth,
      rectY + rectHeight
    )
  );
}

// Function to check if a point is inside a rectangle
function pointInRectangle(px, py, rectX, rectY, rectWidth, rectHeight) {
  return (
    px > rectX &&
    px < rectX + rectWidth &&
    py > rectY &&
    py < rectY + rectHeight
  );
}

// Function to check if two line segments intersect
function lineIntersect(x1, y1, x2, y2, x3, y3, x4, y4) {
  let den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);
  if (den === 0) {
    return false; // Lines are parallel
  }

  let ua =
    ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den;
  let ub =
    ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den;

  return ua >= 0 && ua <= 1 && ub >= 0 && ub <= 1;
}


function parseObject(object) {
  let result = new CustomJSONObject();

  for (let i = 0; i < object.getAttributeCount(); i++) {
    if (object.listAttributes()[i] === "x" || object.listAttributes()[i] === "y") {
      result.setFloat(object.listAttributes()[i], float(object.getString(object.listAttributes()[i])));
    } else {
      result.setString(object.listAttributes()[i], object.getString(object.listAttributes()[i]));
    }
  }

  let k = 0;
  for (let i = 0; i < object.listChildren().length; i++) {
    k = 0;
    if (object.listChildren()[i] !== "#text") {
      if (object.getChildren(object.listChildren()[i])[0].getName() === "value") {
        result.setString("value", object.getChildren(object.listChildren()[i])[0].getContent());
        k = 1;
      }

      for (let j = 0; j < valtag.length; j++) {
        if (object.getChildren(object.listChildren()[i])[0].getName() === valtag[j]) {
          result.setFloat(valtag[j], float(object.getChildren(object.listChildren()[i])[0].getChildren("value")[0].getContent()));
          k = 1;
          break;
        }
      }

      for (let j = 0; j < booltag.length; j++) {
        if (object.getChildren(object.listChildren()[i])[0].getName() === booltag[j]) {
          result.setString(booltag[j], object.getChildren(object.listChildren()[i])[0].getChildren("value")[0].getContent());
          k = 1;
          break;
        }

        if (object.getChildren(object.listChildren()[i])[0].getName() === "type") {
          result.setString("type", object.getChildren(object.listChildren()[i])[0].getString("value"));
          k = 1;
          break;
        }

        if (object.getChildren(object.listChildren()[i])[0].getName() === "graphics") {
          if (object.getChildren(object.listChildren()[i])[0].listChildren().length > 2) {
            let graphics_object = object.getChildren(object.listChildren()[i])[0];
            let coordinate = graphics_object.getChildren(graphics_object.listChildren()[1])[0];
            let values = new CustomJSONArray();
            
            values.add(coordinate.getString(coordinate.listAttributes()[0]));

            if (maxX < coordinate.getString(coordinate.listAttributes()[0])) {
              maxX = coordinate.getString(coordinate.listAttributes()[0]);
            }

            if (minX > coordinate.getString(coordinate.listAttributes()[0])) {
              minX = coordinate.getString(coordinate.listAttributes()[0]);
            }

            values.add(coordinate.getString(coordinate.listAttributes()[1]));

            if (maxY < coordinate.getString(coordinate.listAttributes()[1])) {
              maxY = coordinate.getString(coordinate.listAttributes()[1]);
            }

            if (minY > coordinate.getString(coordinate.listAttributes()[1])) {
              minY = coordinate.getString(coordinate.listAttributes()[1]);
            }

            result.setJSONArray(graphics_object.listChildren()[1], values);
          } else {

          }

          k = 1;
          break;
        }
      }

      if (k === 0) {
        let temp = object.getChildren(object.listChildren()[i])[0];
        result.setJSONObject(object.listChildren()[i], parseObject(temp));
      }
    }
  }

  return result;
}

// Function to prepare the XML file for 

function preparation() {
  
  // Extract the xml structure from the pnml file
  let net = xml.getChildren("net")[0]; // The net is the main object in the pnml file
  let tokens = net.getChildren("token"); // Extract the list of tokens
  let places = net.getChildren("place"); // Extract the list of places
  let transitions = net.getChildren("transition"); // Extract the list of transitions
  let arcs = net.getChildren("arc"); // Extract the list of arcs

  
  Tokenslist=[];
  for (let i = 0; i < tokens.length; i++) {
    let p = new Token(parseObject(tokens[i])); // Construct a place object from one instance in the pnlm file
    p.show();
    Tokens[p.getId()] = p; // Put the Token with its id in the t array
    append(Tokenslist,p.getId());
  }

  for (let i = 0; i < places.length; i++) {
    let p = new Place(parseObject(places[i])); // Construct a place object from one instance in the pnlm file
    Places[p.getId()] = p; // Put the Place with its id in the Places array
  }

  

  for (let i = 0; i < transitions.length; i++) {
    let t = new Transition(parseObject(transitions[i]));// Construct a transition object from one instance in the pnlm file
    Transitions[t.getId()] = t;  // Put the Transition with its id in the Transitions array
  }


  for (let i = 0; i < arcs.length; i++) {
    let a = new Arc(parseObject(arcs[i]));// Construct a arc object from one instance in the pnlm file
    Arcs[a.getId()] = a;  // Put the Arc with its id in the Arcs array
  }

  width_c = ceil(maxX - minX);
  height_c = ceil(maxY - minY);
}
