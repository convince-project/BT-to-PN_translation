from general_support import *
import re

allowHalt=False
outcomes=3
allowed_outcome=0
GlobalOptimization=False
simplified=True
SingleToken=True
showReset=False
counter_nodes=0

TokenTag=["Tick","Halt","Running","Success","Failure","Counter","MS","MF","MR","MC"] # Tag of the various tokens of a Behavior Tree

if SingleToken:
    Tokens=["Default"]
    Outcomes=["Running","Success","Failure"]
    Tags=["T"]
else:
    Tokens=["Tick",
            "Halt",
            "Counter",
            "Running",
            "Success",
            "Failure"]
    Tags=["T","H","A","R","S","F"]


symbols={
    "les":{
        "op":"<",
        "comment":"<"
    },
    "gtr":{
        "op":">",
        "comment":">"
    },
    "gq":{
        "op":"≥",
        "comment":">="
    },
    "eq":{
        "op":"=",
        "comment":"="
    },
    "ne":{
        "op":"",
        "comment":"!="
    },
    "lq":{
        "op":"≤",
        "comment":"<="
    },
    "and":{
        "op":"∧",
        "comment":"&"
    },
    "or":{
        "op":"∨",
        "comment":"|"
    },
    "not":{
        "op":"¬",
        "comment":"!"
    },
}



assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {
                            "left": {},
                            "op": "≥",
                            "right": {}
                        }
                    } 

def construct_guard2(string):
    array=[x for x in re.split(r' & | \(|\) |\(|\)',string) if x]
    new_string=""
    for i in range(1,len(array)):
        if i < len(array)-1:
            new_string+=array[i]+" & "
        else:
            new_string+=array[i]
    components=array[0].split(" ")

    if len(array)>1:
        if len(components)==3:
            try:
                right=int(components[2])
            except:
                right=components[2]
            return {
                    "left": {
                        "left": components[0],
                        "op": symbols[components[1]]["op"],
                        "right": right
                    },
                    "op": symbols["and"]["op"],
                    "right": construct_guard2(new_string)
                }
        else:
            try:
                left=array[1].split(" ")[0]
                op=array[1].split(" ")[1]
                right=int(array[1].split(" ")[2])
            except:
                left=array[1].split(" ")[0]
                op=array[1].split(" ")[1]
                right=array[1].split(" ")[2]
            return {
                "op":symbols[components[0]]["op"],
                "exp":{
                    "left": left,
                    "op": symbols[op]["op"],
                    "right": right
                }
            }
    else:
        try:
            right=int(components[2])
        except:
            right=components[2]

        return {
                    "left": components[0],
                    "op": symbols[components[1]]["op"],
                    "right": right
                }


def construct_guard(string,symbol):
    array=string.split("&")
    if len(array)==1:
        temp_stringL=array[0].split(" ") # left of the first condition
        if int(temp_stringL[3])<1:
            symbol="eq"
        return {
                "left": temp_stringL[1],
                "op": [op[1]["op"] for op in symbols.items() if op[1]["comment"] == temp_stringL[2]][0],
                "right": int(temp_stringL[3])
            }
    elif len(array)==2:
        temp_stringL=array[0].split(" ") # left of the first condition
            
        if int(temp_stringL[3])<1:
            symbol="eq"
        tempL={
                "left": temp_stringL[1],
                "op": [op[1]["op"] for op in symbols.items() if op[1]["comment"] == temp_stringL[2]][0],
                "right": int(temp_stringL[3])
            }
        temp_stringR=array[1].split(" ") # right of the first condition
        if int(temp_stringR[3])<1:
            symbol="eq"
        tempR={
                "left": temp_stringR[1],
                "op": [op[1]["op"] for op in symbols.items() if op[1]["comment"] == temp_stringR[2]][0],
                "right": int(temp_stringR[3])
            }
        return {
                    "left": tempL,
                    "op": symbols["and"]["op"],
                    "right": tempR
                }
    else:
        temp_stringL=array[0].split(" ") # left of the first condition
        if int(temp_stringL[3])<1:
            symbol="eq"
        tempL={
                "left": temp_stringL[1],
                "op": [op[1]["op"] for op in symbols.items() if op[1]["comment"] == temp_stringL[2]][0],
                "right": int(temp_stringL[3])
            }
        temp_stringR=""
        for i in range(1,len(array)):
            if not array[i]=="":
                temp_stringR=temp_stringR+array[i]
                if i < len(array)-1:
                    temp_stringR=temp_stringR+"&"
        tempR=construct_guard(temp_stringR,symbol)
        return {
                    "left": tempL,
                    "op": symbols["and"]["op"],
                    "right": tempR
                }

def construct_prob_assignment(in_vector,out_vector,in_place,out_place,structure,probability=None,memory=False,symbol="eq"):
    temp=structure['automata'][0]['edges']
    edge_template={
                    "destinations": [],
                    "guard":{},
                    "location": "loc"
                  }
    
    
    
    assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {}
                    }
    guard_string=""
    for m in range(len(out_vector)):
        guard_string=""
        destination_template={
                "assignments": [],
                "location": "loc",
                }
        destination_template["comment"]=""
        assignment_vector=[]
        for k in range(2):
            for i in range(len(Tokens)):
                if k==0:
                    ref=in_place+Tags[i]
                    if not memory:
                        value=0
                    else:
                        if memory=="I":
                            if i<2:
                                value=0
                            else:
                                value=ref
                        else:
                            value=0
                    guard_string=guard_string+"( "+ref+" "+symbols[symbol]["comment"]+" "+str(in_vector[i])+" )"
                    if(i<len(Tokens)-1) and len(Tokens)>1:
                        guard_string=guard_string+"&"
                    assignment_vector.append(value)
                else:
                    ref=out_place+Tags[i]
                    value=out_vector[m][i]
                    if not memory[m]:
                        value=out_vector[m][i]
                    else:
                        
                        if memory[m]=="O":
                            if out_vector[0]==1:
                                value=out_vector[m][i]
                            else:
                                if i>2:
                                    if out_vector[m][i]>0:
                                        value=out_vector[m][i]
                                    else:
                                        value=ref
                                else:
                                    value=out_vector[m][i]
                        else:
                            value=out_vector[m][i]
                assignment_template={
                                "comment": " * <- *",
                                "ref": "",
                                "value": {}
                            }
                assignment_template["ref"]=ref
                assignment_template["value"]=value
                assignment_template["comment"]=ref+" <- "+str(value)
                
                destination_template["assignments"].append(assignment_template)

            if k==0:
                destination_template["comment"]=destination_template["comment"]+" guard:"+str(in_vector)
            else:
                destination_template["comment"]=destination_template["comment"]+" "+in_place+":"+str(assignment_vector)
                destination_template["comment"]=destination_template["comment"]+" "+out_place+":"+str(out_vector[m])
            
            if not (len(probability)<2):
                destination_template["probability"]={"exp":probability[m]}
            else:
                destination_template["probability"]={"exp":1}
                # destination_template["probability"]={}
        
        edge_template['destinations'].append(destination_template)
    edge_template['guard']["comment"]=guard_string
    edge_template['guard']["exp"]=construct_guard(guard_string,symbol)
    temp.append(edge_template)
        
    return structure

def construct_halt_assignment(in_vector,out_vector,in_place,out_place,structure,memory=False):
    temp=structure['automata'][0]['edges']
    edge_template={
                    "destinations": [],
                    "guard":{},
                    "location": "loc"
                  }
    assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {}
                    }
    destination_template={
                "assignments": [],
                "location": "loc",
                }
    
    destination_template["comment"]=""
    guard_string=""
    assignment_vector=[]
    for k in range(2):
        
        for i in range(len(Tokens)):
            if k==0:
                ref=in_place+Tags[i]
                symbol="eq"
                value1=in_vector[i]
                
                if not memory:
                    if i>2:
                        value=ref
                    else:
                        value=0
                else:
                    if i<2:
                        value=0
                    else:
                        symbol="eq"
                        if memory=="I" and i>2:
                            if in_vector[i]>0:
                                symbol="gq"
                                value1=0
                            else:
                                symbol="eq"
                                value1=in_vector[i]
                            value=0
                        else:
                            symbol="eq"
                            value=ref

                assignment_vector.append(value)
                guard_string=guard_string+"( "+ref+" "+symbols[symbol]["comment"]+" "+str(value1)+" )"

                if(i<len(Tokens)-1) and len(Tokens)>1:
                    guard_string=guard_string+"&"
            else:
                ref=out_place+Tags[i]
                if memory=="I":
                    if i<2:
                        if i>0:
                            value=1
                        else:
                            value=0
                    else:
                        value=0
                else:    
                    if i>2:
                        value=ref
                    else:
                        value=out_vector[i]
                
                
            assignment_template={
                            "comment": " * <- *",
                            "ref": "",
                            "value": {}
                        }
            assignment_template["ref"]=ref
            assignment_template["value"]=value
            assignment_template["comment"]=ref+" <- "+str(value)
            
            destination_template["assignments"].append(assignment_template)
            destination_template["probability"]={"exp":1}
            # destination_template["probability"]={}
        if k==0:
                destination_template["comment"]=destination_template["comment"]+" guard:"+str(in_vector)
        else:
            destination_template["comment"]=destination_template["comment"]+" "+in_place+":"+str(assignment_vector)
            destination_template["comment"]=destination_template["comment"]+" "+out_place+":"+str(out_vector)
    edge_template['guard']["comment"]=guard_string
    edge_template['guard']["exp"]=construct_guard(guard_string,symbol)
    edge_template['destinations'].append(destination_template)
    temp.append(edge_template)
        
    return structure

def replace_not_conditions(s):
    def replacement(match):
        var, val = match.groups()
        if val is None:
            val = 0  # default value if no 'a' specified
        else:
            val = int(val)
        return f"{var}<{int(val)+1}"

def repl_not(match):
    expr = match.group(1)
    if '=' in expr:
        var, val = expr.split('=')
        return f"{var.strip()}<{int(val.strip())}"
    else:
        var = expr.strip()
        return f"{var}<1"  # 0+1 = 1 (default case)
    
def replace_reset_conditions(s):
    def replacement(match):
        var, val = match.groups()
        val=0
        return f"{var}<-0"

def repl_reset(match):
    expr = match.group(1)
    var = expr.strip()
    return f"{var}<-0"  # 0+1 = 1 (default case)

# Main replacement function




def create_assignment(guard,result,priority,structure):


    # Convert to dictionaries for easy lookup
    dict1 = dict(re.findall(r'(\S+?)=(\S+)',guard))
    dict2 = dict(re.findall(r'(\S+?)=(\S+)',result))

    # Find common keys
    common_keys = set(dict1.keys()) & set(dict2.keys())

    # Extract matching tuples
    matching_tuples = [(key, dict1[key]) for key in common_keys]

    temp=structure['automata'][0]['edges']
    edge_template={
                    "destinations": [],
                    "guard":{},
                    "location": "loc",
                    "priority":{"expression":0}
                  }
    
    
    destination_template={
                "assignments": [],
                "location": "loc",
                }
    
    assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {}
                    }
    
    # Construct the guard

    guard = re.sub(r'not\(\s*(.*?)\s*\)', repl_not, guard)
    result = re.sub(r'R\(\s*(.*?)\s*\)', repl_reset, result)

    array=re.split(r'(=|\+=|>=|<| & )',guard)

    guard_string="("
    guard_variables=[]
    assignment_variables=[]
    op_variables=[]
    for p in range(len(array)-1):
        if p==0:
            guard_variables.append(array[p])
            op_variables.append(array[p+1])
            assignment_variables.append(array[p+2])
        if array[p+1]==" & ":
            guard_string+=array[p]+") "
        elif array[p]==" & ":
            guard_string+=array[p]+" ("
            guard_variables.append(array[p+1])
            op_variables.append(array[p+2])
            assignment_variables.append(array[p+3])
        elif array[p]=="=":
            guard_string+="gq "
        elif array[p]==">=":
            guard_string+="gq "
        elif array[p]=="<":
            guard_string+="les "
        else:    
            guard_string+=array[p]+" "
    guard_string+=array[len(array)-1]+")"
    for i in range(len(guard_variables)):
        if not guard_variables[i] in common_keys:
            assignment_template1=copy.copy(assignment_template)
            assignment_template1["ref"]=guard_variables[i]
            if op_variables[i]=="<":
                continue
            else:
                assignment_template1["value"]={'left': guard_variables[i] ,'op': '-','right': int(assignment_variables[i])}
                assignment_template1["comment"]=guard_variables[i]+" <- "+guard_variables[i]+" - "+assignment_variables[i]
            destination_template["assignments"].append(assignment_template1)
    edge_template['guard']["exp"]=construct_guard2(guard_string)

    # Construct the assignments
    array=re.split(r'(<-|=|>=| & )',result)
    guard_string="("
    guard_variables=[]
    assignment_variables=[]
    op_variables=[]
    for p in range(len(array)-1):
        if p==0:
            guard_variables.append(array[p])
            op_variables.append(array[p+1])
            assignment_variables.append(array[p+2])

        if array[p+1]==" & ":
            guard_string+=array[p]+") "
        elif array[p]==" & ":
            guard_string+=array[p]+" ("
            guard_variables.append(array[p+1])
            op_variables.append(array[p+2])
            assignment_variables.append(array[p+3])
        elif array[p]=="=":
            guard_string+="eq "
        elif array[p]==">=":
            guard_string+="gq "
        else:    
            guard_string+=array[p]+" "
    
    guard_string+=array[len(array)-1]+")"
    
    for i in range(len(guard_variables)):
        assignment_template1=copy.copy(assignment_template)
        assignment_template1["ref"]=guard_variables[i]
        if op_variables[i]=="<-":
            assignment_template1["value"]=0
            assignment_template1["comment"]=guard_variables[i]+" <- "+assignment_variables[i]
        else:
            if guard_variables[i] in common_keys:
                assignment_variables[i]=str(-int(dict1[guard_variables[i]])+int(dict1[guard_variables[i]]))
            try:
                right={'left': guard_variables[i] ,'op': '+','right': int(assignment_variables[i])}
            except:
                
                parts=assignment_variables[i].split("+")
                
                right={
                    "left":parts[0],
                    "op":"+",
                    "right":{
                        "left":parts[0],
                        "op":"+",
                        "right":int(parts[1])
                    }
                }
                #right=assignment_variables[i]
            
            assignment_template1["value"]=right
            assignment_template1["comment"]=guard_variables[i]+" <- "+ guard_variables[i]+" + "+assignment_variables[i]
        destination_template["assignments"].append(assignment_template1)
    edge_template["destinations"].append(destination_template)
    edge_template["priority"]["expression"]=priority
    
    edge_template["location"]="loc"
    temp.append(edge_template)

def create_final_assignment(in_vector,out_vector,in_place,out_place,structure):
    temp=structure['automata'][0]['edges']
    edge_template={
                    "destinations": [],
                    "guard":{},
                    "location": "loc"
                  }
    assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {}
                    }
    destination_template={
                "assignments": [],
                "location": "loc",
                }
    
    destination_template["comment"]=""
    guard_string=""
    assignment_vector=[]
    for k in range(2):
        
        for i in range(len(Tokens)):
            if k==0:
                ref=in_place+Tags[i]
                symbol="gq"
                if i>1:
                    value1=in_vector[i]
                else:
                    value1=0
                value=0
                assignment_vector.append(value)
                guard_string=guard_string+"( "+ref+" "+symbols[symbol]["comment"]+" "+str(value1)+" )"

                if(i<len(Tokens)-1) and len(Tokens)>1:
                    guard_string=guard_string+"&"
            else:
                ref=out_place+Tags[i]
                value=out_vector[i]
            assignment_template={
                            "comment": " * <- *",
                            "ref": "",
                            "value": {}
                        }
            assignment_template["ref"]=ref
            assignment_template["value"]=value
            assignment_template["comment"]=ref+" <- "+str(value)
            
            destination_template["assignments"].append(assignment_template)
            destination_template["probability"]={"exp":1}
            # destination_template["probability"]={}
        if k==0:
                destination_template["comment"]=destination_template["comment"]+" guard:"+str(in_vector)
        else:
            destination_template["comment"]=destination_template["comment"]+" "+in_place+":"+str(assignment_vector)
            destination_template["comment"]=destination_template["comment"]+" "+out_place+":"+str(out_vector)
    edge_template['guard']["comment"]=guard_string
    edge_template['guard']["exp"]=construct_guard(guard_string,symbol)
    edge_template['destinations'].append(destination_template)
    temp.append(edge_template)
        
    return structure

def construct_assignment(in_vector,out_vector,in_place,out_place,structure,memory=False):
    temp=structure['automata'][0]['edges']
    edge_template={
                    "destinations": [],
                    "guard":{},
                    "location": "loc"
                  }
    assignment_template={
                        "comment": " * <- *",
                        "ref": "",
                        "value": {}
                    }
    destination_template={
                "assignments": [],
                "location": "loc",
                }
    
    destination_template["comment"]=""
    guard_string=""
    assignment_vector=[]
    
    for k in range(2):
        
        for i in range(len(Tokens)):
            if k==0:
                ref=in_place+Tags[i]
                
                symbol="eq"
                if not memory:
                    value=0
                else:
                    
                    if memory=="I":
                        if i<2:
                            value=0
                        else:
                            
                            if in_vector[0]==0:
                                # symbol="gq"
                                symbol="gq"
                                if in_vector[i]>0:
                                    value=0
                                else:
                                    symbol="gq"
                                    value=ref
                            else:
                                value=ref
                    else:
                        value=0
                assignment_vector.append(value)
                guard_string=guard_string+"( "+ref+" "+symbols[symbol]["comment"]+" "+str(in_vector[i])+" )"
                if(i<len(Tokens)-1) and len(Tokens)>1:
                    guard_string=guard_string+"&"
            else:
                ref=out_place+Tags[i]
                if memory=="O":
                    if i<2:
                        value=out_vector[i]
                    else:
                        value=ref
                else:
                    value=out_vector[i]

            assignment_template={
                            "comment": " * <- *",
                            "ref": "",
                            "value": {}
                        }
            assignment_template["ref"]=ref
            assignment_template["value"]=value
            assignment_template["comment"]=ref+" <- "+str(value)
            
            destination_template["assignments"].append(assignment_template)
            destination_template["probability"]={"exp":1}
            # destination_template["probability"]={}
        if k==0:
                destination_template["comment"]=destination_template["comment"]+" guard:"+str(in_vector)
        else:
            destination_template["comment"]=destination_template["comment"]+" "+in_place+":"+str(assignment_vector)
            destination_template["comment"]=destination_template["comment"]+" "+out_place+":"+str(out_vector)
    edge_template['guard']["comment"]=guard_string
    edge_template['guard']["exp"]=construct_guard(guard_string,symbol)
    edge_template['destinations'].append(destination_template)
    temp.append(edge_template)
        
    return structure

def parseVector(string,dictionary):
    array=string.split(",")
    output=[]
    for i in array:
        output.append(eval(str(i),dictionary))
    return output
    
def MarkingString(vector):
    stringTo=""
    for i in Tokens:
        if SingleToken:
            stringTo= str(vector[Tokens.index(i)]) #stringTo+i+","+#
        else:
            stringTo=stringTo+i+","+str(vector[Tokens.index(i)])
        if Tokens.index(i)<len(Tokens)-1:
            stringTo=stringTo+","
    return stringTo

def createPT(Templates,type,reference,index=-1,TickHalt="",fullname=True):
    if type=="place":
        short="P"+TickHalt
    elif type=="reset":
        short="R"+TickHalt
        type="transition"
    elif type=="interface":
        short="I"+TickHalt
        type="interface"
    else:
        short="T"+TickHalt
    newplace=modifyTemplate(Templates,type,"name/value",generate_name(reference,short,index,fullname),"text")
    newplace.attrib={'id':generate_name(reference,short,index,fullname)}
    return newplace

def createPT1(Templates,type,name,TickHalt="",fullname=True):
    if type=="place":
        short="P"+TickHalt
    elif type=="reset":
        short="R"+TickHalt
        type="transition"
    elif type=="interface":
        
        short="I"+TickHalt
        type="interface"
    else:
        short="T"+TickHalt
    newplace=modifyTemplate(Templates,type,"name/value",name,"text")
    newplace.attrib={'id':name}
    return newplace

def generateArc(Templates,source,target,type,inscription):
    if type=="normal":
        new=findElementbyID(Templates,"N-arc")[0]
    elif type=="inhibitor":
        new=findElementbyID(Templates,"I-arc")[0]
    else:
        new=findElementbyID(Templates,"R-arc")[0]
    new=copy.deepcopy(new)
    new.attrib={'id':source+" to "+target,'source':source,'target':target}
    new=modifyField(new,"inscription/value",MarkingString(inscription),"text")
    new.attrib={'id':source+" to "+target,'source':source,'target':target}
    return new

