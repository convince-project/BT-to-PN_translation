let arc_arrowsize = 10;
let arc_trianglesize = 10;
let arc_ellipse = 10;

class Arc {
  constructor(json) {
    this.tagged = json.getString("tagged");
    this.probability = json.getFloat("probability");
    this.inscriptionstring = json.getString("inscription");
    let splitted=splitTokens(this.inscriptionstring,",");
    this.inscription=new Map();
    if(splitted.length<2){
      this.inscription.set(Tokenslist[0],int(splitted));
    }else{
      for(let i =0;i<splitted.length;i++){
        this.inscription.set(splitted[i],int(splitted[i+1]));
        i++;
      }
    }
    this.id = json.getString("id");
    this.source = json.getString("source");
    
    this.type = json.getString("type");
    this.target = json.getString("target");
    
    if (Places.hasOwnProperty(this.source)) {
      Places[this.source].AddArc(this,"output");
      Transitions[this.target].AddArc(this,"input");
    }else{
      Places[this.target].AddArc(this,"input");
      Transitions[this.source].AddArc(this,"output");
    }
    
    this.status = 0;
  }

  // Getter methods
  getTagged() {
    return this.tagged;
  }

  getProbability() {
    return this.probability;
  }

  getInscription() {
    return this.inscription;
  }

  getId() {
    return this.id;
  }

  getSource() {
    return this.source;
  }

  getType() {
    return this.type;
  }

  getTarget() {
    return this.target;
  }

  update(){
    if (Places.hasOwnProperty(this.source)) {
      let tempcounter1=0; //count how many marking tokens surpass the inscription threshold
      let tempcounter2=0; // count how many tokens in the inscription are more than 0;
      for(let i=0;i<Tokenslist.length;i++){
        if(int(this.inscription.get(Tokenslist[i]))<=int(Places[this.source].tokens.get(Tokenslist[i])) && int(this.inscription.get(Tokenslist[i]))>0){
          tempcounter1++;
          tempcounter2++;
        }else if(int(this.inscription.get(Tokenslist[i]))>int(Places[this.source].tokens.get(Tokenslist[i]))){
          this.status=0;
          tempcounter2++;
          break;
        }
        
      }
      
      if(tempcounter1==tempcounter2){
        this.status=1;
      }
    }else{
        if(Transitions[this.source].status==1){
          this.status=1;
        }else{
          this.status=0;
        }
      
    }
  }

  show() {
    // Example usage:

    // Accessing the properties of the custom object
    console.log("Tagged: " + this.getTagged());
    console.log("Probability: " + this.getProbability());
    console.log("Inscription Value: " + this.getInscription());
    console.log("ID: " + this.getId());
    console.log("Source: " + this.getSource());
    console.log("Type: " + this.getType());
    console.log("Target: " + this.getTarget());
  }

  paint() {
    // Example usage:

    let circleX, circleY;
    let rectX, rectY, rectWidth, rectHeight;
    let lineX1, lineY1, lineX2, lineY2;

    // Find intersection points

    let p = 0; // 0 indicates that the source is a place, 1 the source is an intersection
    if (Places.hasOwnProperty(this.source)) {
      circleX = Places[this.source].getPosition().x;
      circleY = Places[this.source].getPosition().y;
      rectX = Transitions[this.target].getPosition().x;
      rectY = Transitions[this.target].getPosition().y;
      p = 1;
    } else {
      circleX = Places[this.target].getPosition().x;
      circleY = Places[this.target].getPosition().y;
      rectX = Transitions[this.source].getPosition().x;
      rectY = Transitions[this.source].getPosition().y;
    }
    paintMarking(this.inscription,(circleX+rectX)/2,(circleY+rectY)/2);
    lineX1 = circleX;
    lineY1 = circleY;
    lineX2 = rectX;
    lineY2 = rectY;

    let a = findIntersections(
      lineX1,
      lineY1,
      lineX2,
      lineY2,
      rectX,
      rectY,
      transition_width / 2,
      transition_height / 2
    ); // rectangle intersection
    let b = findIntersection(
      lineX1,
      lineY1,
      lineX2,
      lineY2,
      circleX,
      circleY,
      place_radius / 2
    ); // circle intersection
    
    if (this.status === 0) {
      stroke(0);
      fill(0);
    } else if(this.status==1)  {
      stroke(255, 0, 0);
      fill(255, 0, 0);
    }else{
      stroke(0, 0, 255);
      fill(0, 0, 255);
    }
    for (let j = 0; j < 4; j++) {
      if (a[j] !== null) {
        line(float(a[j].x), float(a[j].y), float(b[0].x), float(b[0].y));
        if (p === 1) {
          let diff = p5.Vector.sub(a[j], b[0]);
          if (this.type === "normal") {
            
            let symCoor = p5.Vector.add(b[0], diff);
            let angle = float(diff.heading());
            let x2 = float(symCoor.x);
            let y2 = float(symCoor.y);
            let arrowX1 = x2 - arc_trianglesize * cos(angle - PI / 6);
            let arrowY1 = y2 - arc_trianglesize * sin(angle - PI / 6);
            let arrowX2 = x2 - arc_trianglesize * cos(angle + PI / 6);
            let arrowY2 = y2 - arc_trianglesize * sin(angle + PI / 6);
            // Draw arrowhead (triangle)
            triangle(x2, y2, arrowX1, arrowY1, arrowX2, arrowY2);
          } else if (this.type === "inhibitor") {
            diff.mult((diff.mag() - arc_ellipse / 2) / diff.mag());
            let symCoor = p5.Vector.add(b[0], diff);
            ellipse(
              symCoor.x - arc_ellipse / 2,
              symCoor.y - arc_ellipse / 2,
              arc_ellipse,
              arc_ellipse
            );
          } else {
            diff.mult(
              (diff.mag() - arc_arrowsize * sqrt(2)) / diff.mag()
            );
            push();
            let symCoor = p5.Vector.add(b[0], diff);
            translate(symCoor.x, symCoor.y);
            rotate(diff.heading() - PI / 4);
            rect(0, 0, arc_arrowsize, arc_arrowsize);
            pop();
          }
        } else {
          let diff = p5.Vector.sub(b[0], a[j]);
          if (this.type === "normal") {
            let symCoor = p5.Vector.add(a[j], diff);
            let angle = diff.heading();
            let x2 = symCoor.x;
            let y2 = symCoor.y;
            let arrowX1 = x2 - arc_trianglesize * cos(angle - PI / 6);
            let arrowY1 = y2 - arc_trianglesize * sin(angle - PI / 6);
            let arrowX2 = x2 - arc_trianglesize * cos(angle + PI / 6);
            let arrowY2 = y2 - arc_trianglesize * sin(angle + PI / 6);
            // Draw arrowhead (triangle)
            triangle(x2, y2, arrowX1, arrowY1, arrowX2, arrowY2);
          } else if (this.type === "inhibitor") {
            diff.mult((diff.mag() - 5) / diff.mag());
            let symCoor = p5.Vector.add(a[j], diff);
            ellipse(
              symCoor.x - arc_ellipse / 2,
              symCoor.y - arc_ellipse / 2,
              arc_ellipse,
              arc_ellipse
            );
          } else {
            diff.mult(
              (diff.mag() - arc_arrowsize * sqrt(2)) / diff.mag()
            );
            push();
            let symCoor = p5.Vector.add(a[j], diff);
            translate(symCoor.x, symCoor.y);
            rotate(diff.heading() - PI / 4);
            rect(0, 0, arc_arrowsize, arc_arrowsize);
            pop();
          }
        }
        fill(0);
        stroke(0);
      }
    }
  }
}

Arc.prototype.tagged = 0;
Arc.prototype.probability = 1;
Arc.prototype.inscriptionstring = "";
Arc.prototype.inscription=[];
Arc.prototype.id = "";
Arc.prototype.source = "";
Arc.prototype.type = "";
Arc.prototype.target = "";
Arc.prototype.status = 0;

function findSegmentIntersection(x1, y1, x2, y2, x3, y3, x4, y4) {
  let intersection = createVector();

  let den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1);

  if (den === 0) {
    // Segments are parallel or coincident
    return null;
  }

  let ua =
    ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den;
  let ub =
    ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den;

  if (ua >= 0 && ua <= 1 && ub >= 0 && ub <= 1) {
    // Intersection point lies within both segments
    intersection.x = x1 + ua * (x2 - x1);
    intersection.y = y1 + ua * (y2 - y1);
    return intersection;
  }

  // No intersection point found
  return null;
}

function findIntersections(x1, y1, x2, y2, rx, ry, rw, rh) {
  let intersections = Array(4).fill(null);

  // Calculate intersections with each side of the rectangle
  intersections[0] = findSegmentIntersection(
    x1,
    y1,
    x2,
    y2,
    rx - rw,
    ry - rh,
    rx + rw,
    ry - rh
  ); // Top side
  intersections[1] = findSegmentIntersection(
    x1,
    y1,
    x2,
    y2,
    rx + rw,
    ry - rh,
    rx + rw,
    ry + rh
  ); // Right side
  intersections[2] = findSegmentIntersection(
    x1,
    y1,
    x2,
    y2,
    rx - rw,
    ry + rh,
    rx + rw,
    ry + rh
  ); // Bottom side
  intersections[3] = findSegmentIntersection(
    x1,
    y1,
    x2,
    y2,
    rx - rw,
    ry - rh,
    rx - rw,
    ry + rh
  ); // Left side

  return intersections;
}

function findIntersection(x1, y1, x2, y2, cx, cy, r) {
  let intersections = Array(2).fill(null);

  // Vector representing the line segment
  let d = createVector(x2 - x1, y2 - y1);

  // Vector from the line segment start point to the circle center
  let f = createVector(x1 - cx, y1 - cy);

  // Calculate coefficients for the quadratic equation
  let a = d.dot(d);
  let b = 2 * f.dot(d);
  let c = f.dot(f) - r * r;

  // Calculate discriminant
  let discriminant = b * b - 4 * a * c;

  if (discriminant >= 0) {
    // Calculate two possible values for t (parameter along the line)
    let t1 = (-b + sqrt(discriminant)) / (2 * a);
    let t2 = (-b - sqrt(discriminant)) / (2 * a);

    // Calculate intersection points
    intersections[0] = createVector(x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1));
    intersections[1] = createVector(x1 + t2 * (x2 - x1), y1 + t2 * (y2 - y1));
  }

  return intersections;
}
