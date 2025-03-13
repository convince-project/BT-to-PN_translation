from PN_support import *
import general_support as gs
import numpy

P=Digraph(format='gv')
P.engine=engine_list[0]
F=Digraph(format='gv')
F.engine="dot"

Unsumm_nodes=[]
Aux_nodes=[]
Not_Optimized=[]
Inf_arcs=[]
variables=[]
node_counter=0


class Transition:
    def __init__(self,pre,post,priority=1,inferred=False):
        global P,Unsumm_nodes,Inf_arcs,variables
        self.name=f"{pre} -> {post}"
        if inferred:
            P.edge(pre,post,str(priority),color='green')
            Inf_arcs.append(self.name)
        else:
            P.edge(pre,post,str(priority))

# Reactive nodes
def CreateReactiveNode(tree,name,node_type,optimization=False):
    variables.append(name+"_T")
    variables.append(name+"_H")
    variables.append(name+"_S")
    variables.append(name+"_F")
    variables.append(name+"_R")
    variables.append(name+"_A")
    variables.append(name+"_Temp_R")
    if node_type=="S":
        other_type="F"
    else:
        other_type="S"
    variables.append(name+"_Temp_"+other_type)

    Transition(name+"_T=1",name+"0_T=1")
    Transition(name+"_H=1",name+"0_H=1")
    Transition(f"not({name}_N=4)",f"R({name}_M)")
    for i in tree:
        child_code=name+str(list(tree).index(i))
        successor_code=name+str(list(tree).index(i)+1)
        # For all the children except the last
        if list(tree).index(i)<len(tree)-1:
            # Case where the child returns the continuation response
            Transition(f"{child_code}_{node_type}=1",f"{successor_code}_T=1")
            # Case where the next child returns running
            Transition(f"{child_code}_R=1",f"{name}_Temp_R=1 & {successor_code}_H=1")
            # Case where the child returns the non continuing condition
            Transition(f"{child_code}_{other_type}=1",f"{name}_Temp_{other_type}=1 & {successor_code}_H=1")
            # Case where the child returns an acknowledgement after being halted
            Transition(f"{child_code}_A=1",f"{successor_code}_H=1")
            # Inferred transition from the temporary nodes and halt to the successor with halt
            Transition(f"{name}_Temp_R=1 & {successor_code}_H=1",f"{successor_code}_H=1",inferred=True)
            Aux_nodes.append(f"{name}_Temp_R=1 & {successor_code}_H=1")
            Transition(f"{name}_Temp_{other_type}=1 & {successor_code}_H=1",f"{successor_code}_H=1",inferred=True)
            Aux_nodes.append(f"{name}_Temp_{other_type}=1 & {successor_code}_H=1")
            
        else:
            Transition(f"{child_code}_"+node_type+"=1",name+"_"+node_type+"=1")
            Transition(child_code+"_R=1",name+"_R=1")
            Transition(child_code+"_A=1",name+"_A=1")
            Transition(child_code+"_A=1",name+"_Temp_"+other_type+"=1 & "+ child_code+"_A=1",inferred=True)
            Aux_nodes.append(name+"_Temp_"+other_type+"=1 & "+ child_code+"_A=1")
            Transition(child_code+"_A=1",name+"_Temp_R=1 & "+ child_code+"_A=1",inferred=True)
            Aux_nodes.append(name+"_Temp_R=1 & "+ child_code+"_A=1")
            Transition(name+"_Temp_"+other_type+"=1 & "+ child_code+"_A=1",name+"_"+other_type+"=1",priority=2)# ,label='2')
            Transition(child_code+"_"+other_type+"=1",name+"_"+other_type+"=1")
            Transition(name+"_Temp_R=1 & "+ child_code+"_A=1",name+"_R=1", priority=2) #,label='2')
    

# RetryUntilSuccessful
def CreateRetryUntilSuccessful(tree,name,iterations):
    global P,Unsumm_nodes,Inf_arcs,variables

    P.edge(name+"_T=1",name+"0_T=1")
    Unsumm_nodes.append(name+"0_T=1")
    P.edge(name+"0_S=1",name+"_S=1")
    P.edge(name+"0_F=1",name+"_Temp="+name+"_Temp"+"+1 & "+name+"0_T=1")
    P.edge(name+"0_R=1",name+"_Temp="+name+"_Temp"+"+1 & "+name+"0_T=1")
    
    P.edge(name+"_Temp="+name+"_Temp"+"+1 & "+name+"0_T=1",name+"0_T=1",color="green")
    Inf_arcs.append("\""+name+"_Temp="+name+"_Temp"+"+1 & "+name+"0_T=1\" -> \""+name+"0_T=1\"")
    Unsumm_nodes.append(name+"_Temp="+name+"_Temp"+"+1 & "+name+"0_T=1")
    Unsumm_nodes.append(name+"0_T=1 & "+name+"_Temp="+str(iterations))
    P.edge(name+"0_T=1 & "+name+"_Temp="+str(iterations),name+"_F=1")
    P.edge(name+"0_T=1",name+"0_T=1 & "+name+"_Temp="+str(iterations),color="green")
    Inf_arcs.append("\""+name+"0_T=1\" -> \""+name+"0_T=1 & "+name+"_Temp="+str(iterations)+"\"")

    P.edge(name+"_H=1",name+"0_H=1")
    P.edge(name+"0_A=1",name+"_A=1")

# Switch2

def CreateSwitch2(tree,name,optimization=False):
    global P,Unsumm_nodes,Inf_arcs,variables


    CreateReactiveNode(tree,name,"F",optimization)
    CreateReactiveNode(tree,name+"0","S",optimization)
    CreateCondition(tree,name+"00",optimization)
    CreateReactiveNode(tree[0],name+"01","S",optimization)
    CreateReactiveNode(tree[1],name+"1","S",optimization)
    
# Nodes with memory
def CreateMemoryNode(tree,name,node_type):
    global P,Unsumm_nodes,Inf_arcs,variables

    variables.append(name+"_T")
    variables.append(name+"_H")
    variables.append(name+"_S")
    variables.append(name+"_F")
    variables.append(name+"_R")
    variables.append(name+"_A")
    variables.append(name+"_M")
    

    if node_type=="S":
        other_type="F"
    else:
        other_type="S"
    P.edge(name+"_H=1",name+"0_H=1","")
    for i in tree:
        Unsumm_nodes.append(name+"_M="+str(list(tree).index(i))+" & "+name+"_"+other_type+"=1")
        Unsumm_nodes.append(name+"_M="+str(list(tree).index(i))+" & "+name+"_T=1")

        P.edge(name+"_T=1",name+"_M="+str(list(tree).index(i))+" & "+name+"_T=1","",color="green")
        P.edge(name+str(list(tree).index(i))+"_"+other_type+"=1",name+"_M="+str(list(tree).index(i))+" & "+name+"_"+other_type+"=1","")

        Inf_arcs.append(name+"_T=1->"+name+"_M="+str(list(tree).index(i))+" & "+name+"_T=1")
        P.edge(name+"_M="+str(list(tree).index(i))+" & "+name+"_T=1",name+str(list(tree).index(i))+"_T=1","")
        if list(tree).index(i)<len(tree)-1:
            P.edge(name+str(list(tree).index(i))+"_"+node_type+"=1",name+str(list(tree).index(i)+1)+"_T=1","")
            P.edge(name+str(list(tree).index(i))+"_A=1",name+str(list(tree).index(i)+1)+"_H=1","")
        else:
            P.edge(name+str(list(tree).index(i))+"_"+node_type+"=1",name+"_"+node_type+"=1","")
            P.edge(name+str(list(tree).index(i))+"_A=1",name+"_A=1","")
        P.edge(name+str(list(tree).index(i))+"_R=1",name+"_R=1","")
        
        P.edge(name+"_M="+str(list(tree).index(i))+" & "+name+"_"+other_type+"=1",name+"_"+other_type+"=1","",color="green")
        Inf_arcs.append(name+"_M="+str(list(tree).index(i))+" & "+name+"_"+other_type+"=1->"+name+"_"+other_type+"=1")

# Parallel

def CreateParallel(tree,name):
    global P,Unsumm_nodes,Inf_arcs,variables
    variables.append(name+"_T")
    variables.append(name+"_H")
    variables.append(name+"_S")
    variables.append(name+"_F")
    variables.append(name+"_R")
    variables.append(name+"_A")
    variables.append(name+"_CS")
    variables.append(name+"_CF")
    variables.append(name+"_CR")
    variables.append(name+"_NC")

    P.edge(name+"_T=1",name+"0_T=1","")
    P.edge(name+"_H=1",name+"0_H=1","")
    for i in tree:
        if list(tree).index(i)<len(tree)-1:
            P.edge(name+str(list(tree).index(i))+"_A=1",name+str(list(tree).index(i)+1)+"_H=1","")

            P.edge(name+"_NC+=1 & "+name+"_CR+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+"_NC+=1 & "+name+"_CR+=1","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CS+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+"_NC+=1 & "+name+"_CS+=1","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CF+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+"_NC+=1 & "+name+"_CF+=1","",color="green")
            
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CR+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+"_NC+=1 & "+name+"_CR+=1")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CS+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+"_NC+=1 & "+name+"_CS+=1")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CT+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+"_NC+=1 & "+name+"_CF+=1")
            # P.edge(name+"_NC="+str(list(tree).index(i)+1),name+str(list(tree).index(i)+1)+"_T=1","")
            # P.edge(name+str(list(tree).index(i))+"_S=1",name+str(list(tree).index(i)+1)+"_T=1","")
            # P.edge(name+str(list(tree).index(i))+"_R=1",name+str(list(tree).index(i)+1)+"_T=1","")
            # P.edge(name+str(list(tree).index(i))+"_F=1",name+str(list(tree).index(i)+1)+"_T=1","")

            P.edge(name+str(list(tree).index(i))+"_R=1",name+"_NC+=1 & "+name+"_CR+=1 & "+name+str(list(tree).index(i)+1)+"_T=1","")
            P.edge(name+str(list(tree).index(i))+"_S=1",name+"_NC+=1 & "+name+"_CS+=1 & "+name+str(list(tree).index(i)+1)+"_T=1","")
            P.edge(name+str(list(tree).index(i))+"_F=1",name+"_NC+=1 & "+name+"_CF+=1 & "+name+str(list(tree).index(i)+1)+"_T=1","")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CR+=1")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CS+=1")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CF+=1")

            P.edge(name+"_NC+=1 & "+name+"_CR+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+str(list(tree).index(i)+1)+"_T=1","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CS+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+str(list(tree).index(i)+1)+"_T=1","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CF+=1 & "+name+str(list(tree).index(i)+1)+"_T=1",name+str(list(tree).index(i)+1)+"_T=1","",color="green")

            
            
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CR+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+str(list(tree).index(i)+1)+"_T=1")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CS+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+str(list(tree).index(i)+1)+"_T=1")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CT+=1 & "+name+str(list(tree).index(i)+1)+"_T=1->"+name+str(list(tree).index(i)+1)+"_T=1")
            
        else:
            P.edge(name+str(list(tree).index(i))+"_A=1",name+"_A=1","")


            P.edge(name+str(list(tree).index(i))+"_R=1",name+"_NC+=1 & "+name+"_CR+=1","")
            P.edge(name+str(list(tree).index(i))+"_S=1",name+"_NC+=1 & "+name+"_CS+=1","")
            P.edge(name+str(list(tree).index(i))+"_F=1",name+"_NC+=1 & "+name+"_CF+=1","")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CR+=1")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CS+=1")
            Unsumm_nodes.append(name+"_NC+=1 & "+name+"_CF+=1")



            Unsumm_nodes.append(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0")
            Unsumm_nodes.append(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")
            Unsumm_nodes.append(name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")

            P.edge(name+"_NC+=1 & "+name+"_CR+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CS+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CF+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CR+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CS+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CF+=1",name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CR+=1",name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CS+=1",name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")
            P.edge(name+"_NC+=1 & "+name+"_CF+=1",name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0","",color="green")

            Inf_arcs.append(name+"_NC+=1 & "+name+"_CR+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CS+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CF+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0")

            Inf_arcs.append(name+"_NC+=1 & "+name+"_CR+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CS+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CF+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")

            Inf_arcs.append(name+"_NC+=1 & "+name+"_CR+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CS+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")
            Inf_arcs.append(name+"_NC+=1 & "+name+"_CF+=1->"+name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0")



            P.edge(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS>=K & "+name+"_CR>=0",name+"_S=1","")
            P.edge(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0",name+"_F=1","")
            P.edge(name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0",name+"_R=1","")
            Inf_arcs.append(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CS=K & "+name+"_CR>=0->"+name+"_S=1")
            Inf_arcs.append(name+"_NC="+str(list(tree).index(i)+1)+" & "+name+"_CF="+str(len(tree))+"-K+1 & "+name+"_CR>=0->"+name+"_F=1")
            Inf_arcs.append(name+"_NC="+str(list(tree).index(i)+1)+" & not "+name+"_CS>=K & not "+name+"_CF>="+str(len(tree))+"-K+1 & "+name+"_CR>=0->"+name+"_R=1")
            
# Inverter

def CreateInverter(tree,name):
    global P,Unsumm_nodes,Inf_arcs,variables
    P.edge(name+"_T=1",name+"0_T=1","")
    P.edge(name+"0_S=1",name+"_F=1","")
    P.edge(name+"0_F=1",name+"_S=1","")
    P.edge(name+"0_R=1",name+"_R=1","")
    P.edge(name+"_H=1",name+"0_H=1","")
    P.edge(name+"0_A=1",name+"_A=1","")

# Force Success

def CreateForceSuccess(tree,name):    
    global P,Unsumm_nodes,Inf_arcs,variables
    P.edge(name+"_T=1",name+"0_T=1","")
    P.edge(name+"0_S=1",name+"_S=1","")
    P.edge(name+"0_F=1",name+"_S=1","")
    P.edge(name+"0_R=1",name+"_R=1","")
    P.edge(name+"_H=1",name+"0_H=1","")
    P.edge(name+"0_A=1",name+"_A=1","")

def CreateForceFailure(tree,name):    
    global P,Unsumm_nodes,Inf_arcs,variables
    P.edge(name+"_T=1",name+"0_T=1","")
    P.edge(name+"0_S=1",name+"_F=1","")
    P.edge(name+"0_F=1",name+"_F=1","")
    P.edge(name+"0_R=1",name+"_R=1","")
    P.edge(name+"_H=1",name+"0_H=1","")
    P.edge(name+"0_A=1",name+"_A=1","")
    
# Condition node

def CreateCondition(tree,name,optimization=True):
    global P,Unsumm_nodes,Inf_arcs,variables

    if "prob" in tree.attrib.keys():
        branches=tree.attrib['prob'].split(",")
    else:
        branches=["1","1","0"]
    
    if "prob" in tree.attrib.keys():
        haltable=tree.attrib['haltable']
    else:
        haltable=True

    P.node(name+"_T=1",name+"_T=1",style="filled",color='lightblue')
    # P.edge(name+"_T=1",name+"_IT=1","",style="dashed")
    variables.append(name+"_T")
    # variables.append(name+"_IT")
    Unsumm_nodes.append(name+"_T=1")
    # Unsumm_nodes.append(name+"_IT=1")

    if not (branches[0]=='0' and optimization):
        P.edge(name+"_T=1",name+"_S=1","1")
        P.node(name+"_S=1",name+"_S=1",style="filled",color='lightblue')
        variables.append(name+"_S")
        Unsumm_nodes.append(name+"_S=1")

    if not (branches[1]=='0' and optimization):
        P.edge(name+"_T=1",name+"_F=1","1")
        P.node(name+"_F=1",name+"_F=1",style="filled",color='lightblue')
        variables.append(name+"_F")
        Unsumm_nodes.append(name+"_F=1")

    if (not optimization or haltable=="True"):
        Unsumm_nodes.append(name+"_H=1")
        # Unsumm_nodes.append(name+"_IH=1")
        Unsumm_nodes.append(name+"_A=1")
        variables.append(name+"_H")
        variables.append(name+"_A")
        # P.edge(name+"_H=1",name+"_IH=1","",style="dashed")
        P.edge(name+"_H=1",name+"_A=1","1")
        
        
# Action nodes

def CreateAction(tree,name,optimization=True):
    global P,Unsumm_nodes,Inf_arcs,variables

    P.node(name+"_T=1",name+"_T=1",style="filled",color='lightblue')
    # P.edge(name+"_T=1",name+"_IT=1","",style="dashed")
    Unsumm_nodes.append(name+"_T=1")
    variables.append(name+"_T")
    # variables.append(name+"_IT")
    if "prob" in tree.attrib.keys():
        branches=tree.attrib['prob'].split(",")
    else:
        branches=["1","1","1"]
    
    if "prob" in tree.attrib.keys():
        haltable=tree.attrib['haltable']
    else:
        haltable=True
    

    
    if  not ( branches[0]=='0' and optimization):
        P.edge(name+"_T=1",name+"_S=1","1")
        P.node(name+"_S=1",name+"_S=1",style="filled",color='lightblue')
        variables.append(name+"_S")
        Unsumm_nodes.append(name+"_S=1")

    
    if  not ( branches[1]=='0' and optimization):
        P.edge(name+"_T=1",name+"_F=1","1")
        P.node(name+"_F=1",name+"_F=1",style="filled",color='lightblue')
        variables.append(name+"_F")
        Unsumm_nodes.append(name+"_F=1")

    
    if  not ( branches[2]=='0' and optimization):
        P.node(name+"_R=1",name+"_R=1",style="filled",color='lightblue')
        variables.append(name+"_R")
        Unsumm_nodes.append(name+"_R=1")
        P.edge(name+"_T=1",name+"_R=1","1")

    
    
    if (not optimization or haltable=="True"):
        # P.edge(name+"_H=1",name+"_IH=1","",style="dashed")
        P.edge(name+"_H=1",name+"_A=1","1")
        variables.append(name+"_H")
        variables.append(name+"_A")
        # variables.append(name+"_IH")
        # Unsumm_nodes.append(name+"_IH=1")
        Unsumm_nodes.append(name+"_H=1")
        Unsumm_nodes.append(name+"_A=1")