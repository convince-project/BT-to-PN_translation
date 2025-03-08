class Token{
  constructor(json){
    print("printing the objsect");
    print(json);
    this.id = json.getString("id");
    this.red = int(json.getString("red"));
    this.green = int(json.getString("green"));
    this.blue = int(json.getString("blue"));
    this.enabled=json.getString("enabled");
    this.c=color(this.red,this.green,this.blue);
    
  }
  
  drawtext(x, y, quantity) {

    fill(this.red,this.green,this.blue);
    text( quantity, x, y);
  }   
  
  getId(){
    return this.id;
  }
  
  show(){
    console.log("id",this.id);
    console.log("Color",this.c);
    console.log("Enabled",this.enabled);
  }
}

Token.prototype.id = "";
Token.prototype.red = 0;
Token.prototype.green = 0;
Token.prototype.blue = 0;
Token.prototype.enabled= 1;

function paintMarking(tokens,x,y){
  let string="";
  let tempArray=[];
  for(let i=0;i<Tokenslist.length;i++){
    if(tokens.get(Tokenslist[i])>0){
      if(string.length==0){
        
        string+=String(int(tokens.get(Tokenslist[i])));
      }else{
        string+=","+String(int(tokens.get(Tokenslist[i])));
      }
      append(tempArray,Tokenslist[i]);
    }
  }
  if(string.length>0){
    if(textWidth(string)>place_radius/zoom){
      textSize(place_radius/textWidth(string)*12/sqrt(zoom));
       x-=(textWidth(string)/2-textWidth(","));
    }else{
      textSize(12/(sqrt(zoom)));
       x-=(textWidth(string))/2-textWidth(",");
    }
    let tempcounter=0;
    
    for(let i=0;i<string.length;i++){
      if(string[i]!=","){
        Tokens[tempArray[tempcounter]].drawtext(x,y,string[i]);
        
      }else{
        fill(0);
        text(",",x,y);
        tempcounter++;
      }
      x+=textWidth(string[i]);
     }
  }
}
