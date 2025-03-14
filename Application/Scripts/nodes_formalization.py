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
    

def CreateRetryUntilSuccessful(tree,name,iterations):

    Transition(name+"_T=1",name+"_T=1 & "+name+"_M=2")
    Transition(name+"_T=1 & "+name+"_M=2",name+"_T=1 & "+name+"_M=1",inferred=True)
    Transition(name+"_T=1 & "+name+"_M=1",name+"0_T=1",priority=2)
    Transition(name+"0_S=1",name+"_S=1 & R("+name+"_M)")
    Transition(name+"0_F=1",name+"_T=1 & "+name+"_M=2")
    Transition(name+"_T=1 & "+name+"_M=1",name+"_T=1 & "+name+"_M="+str(int(tree.attrib["num_attempts"])+1),inferred=True)
    Transition(name+"_T=1 & "+name+"_M="+str(int(tree.attrib["num_attempts"])+1),name+"_F=1 & R("+name+"_M)",priority=3)
    Transition(name+"0_R=1",name+"_R=1 & R("+name+"_M)")
    Transition(name+"_R=1 & R("+name+"_M)",name+"_R=1",inferred=True)
    Transition(name+"_F=1 & R("+name+"_M)",name+"_F=1",inferred=True)
    Transition(name+"_S=1 & R("+name+"_M)",name+"_S=1",inferred=True)
    Transition(name+"_H=1",name+"0_H=1")
    Transition(name+"0_A=1",name+"_A=1")   

    Unsumm_nodes.append(name+"_T=1")
    Unsumm_nodes.append(name+"_T=1 & "+name+"_M=2")
    Unsumm_nodes.append(name+"_T=1 & "+name+"_M="+str(int(tree.attrib["num_attempts"])+1))
    Aux_nodes.append(name+"_R=1 & R("+name+"_M)")
    Aux_nodes.append(name+"_S=1 & R("+name+"_M)")
    Aux_nodes.append(name+"_F=1 & R("+name+"_M)")
    Aux_nodes.append(name+"_T=1 & "+name+"_M=2")
    Aux_nodes.append(name+"_T=1 & "+name+"_M=1")
    Unsumm_nodes.append(name+"_R=1")
    Unsumm_nodes.append(name+"_F=1")
    Unsumm_nodes.append(name+"_S=1")

# Switch2

def CreateSwitch2(tree,name,optimization=False):
    N=2
    Transition(f"{name}_T=1",f"{name}0C_T=1")
    Transition(f"{name}_H=1",f"{name}0_H=1")
    Transition(f"{name}_H=1",f"{name}_H=1 & M0=1",inferred=True)
    Aux_nodes.append(f"{name}_H=1 & M0=1")
    Transition(f"{name}_H=1 & M0=1",f"{name}0_H=1",priority=2)
    Aux_nodes.append(f"{name}0_H=1")

    for i in range(0,N-1):
        CreateCondition(tree,f"{name}{i}C")
        Transition(f"{name}{i}C_S=1",f"{name}{i}C_C=2")
        Aux_nodes.append(f"{name}{i}C_S=1")
        Aux_nodes.append(f"{name}{i}C_C=2")
        if i==N-2:
            Transition(f"{name}{i}C_F=1",f"{name}{N-1}C_C=2")
            Aux_nodes.append(f"{name}{i}C_F=1")
            Aux_nodes.append(f"{name}{N-1}C_C=2")

        else:
            Transition(f"{name}{i}C_F=1",f"{name}{i+1}C_T=1")
            Aux_nodes.append(f"{name}{i}C_F=1")
            Aux_nodes.append(f"{name}{i+1}C_T=1")

        Transition(f"{name}{i}C_C=2",f"{name}{i}C_C=2 & M{i}=1",inferred=True)
        Aux_nodes.append(f"{name}{i}C_C=2")
        Aux_nodes.append(f"{name}{i}C_C=2 & M{i}=1")
        Transition(f"{name}{i}C_C=2 & M{i}=1",f"{name}{i}_T=1",priority=2)
        Transition(f"{name}{i}C_C=2",f"{name}{i}_T=1")
        for j in range(0,N):
            if not i==j:
                Transition(f"{name}{i}C_C=2",f"{name}{i}C_C=1 & M{j}=1",inferred=True)
                Transition(f"{name}{i}C_C=1 & M{j}=1",f"{name}{j}_H=1",priority=2)
                Transition(f"{name}{i}_A=1",f"{name}{i}_A=1 & {name}{j}C_C=1",inferred=True)
                Aux_nodes.append(f"{name}{i}_A=1 & {name}{j}C_C=1")
                Aux_nodes.append(f"{name}{i}C_C=1 & M{j}=1")
                Transition(f"{name}{j}_A=1 & {name}{i}C_C=1",f"{name}{i}_T=1",priority=2)
        Transition(f"{name}{i}_F=1",f"{name}_F=1")
        Transition(f"{name}{i}_S=1",f"{name}_S=1")
        Transition(f"{name}{i}_R=1",f"{name}_R=1 & M{i}=1")
        Aux_nodes.append(f"{name}_R=1 & M{i}=1")
        Transition(f"{name}_R=1 & M{i}=1",f"{name}_R=1",inferred=True)
        Transition(f"{name}{i}_A=1",f"{name}{i+1}_H=1 & R(M{i})")
        Aux_nodes.append(f"{name}{i+1}_H=1 & R(M{i})")
        Transition(f"{name}{i+1}_H=1 & R(M{i})",f"{name}{i+1}_H=1",inferred=True)
        
    # Handling the last node

    Transition(f"{name}{N-1}C_C=2",f"{name}{N-1}C_C=2 & M{N-1}=1",inferred=True)
    Aux_nodes.append(f"{name}{N-1}C_C=2")
    Aux_nodes.append(f"{name}{N-1}C_C=2 & M{N-1}=1")
    Transition(f"{name}{N-1}C_C=2 & M{N-1}=1",f"{name}{N-1}_T=1",priority=2)
    Transition(f"{name}{N-1}C_C=2",f"{name}{N-1}_T=1")
    for j in range(0,N-1):
        if not N-1==j:
            Transition(f"{name}{N-1}C_C=2",f"{name}{N-1}C_C=1 & M{j}=1",inferred=True)
            Aux_nodes.append(f"{name}{N-1}C_C=1 & M{j}=1")
            Transition(f"{name}{N-1}C_C=1 & M{j}=1",f"{name}{j}_H=1",priority=2)
            Transition(f"{name}{N-1}_A=1",f"{name}{N-1}_A=1 & {name}{j}C_C=1",inferred=True)
            Aux_nodes.append(f"{name}{N-1}_A=1 & {name}{j}C_C=1")
            Transition(f"{name}{j}_A=1 & {name}{N-1}C_C=1",f"{name}{N-1}_T=1",priority=2)
    Transition(f"{name}{N-1}_F=1",f"{name}_F=1")
    Transition(f"{name}{N-1}_S=1",f"{name}_S=1")
    Transition(f"{name}{N-1}_R=1",f"{name}_R=1 & M{N-1}=1")
    Transition(f"{name}_R=1 & M{N-1}=1",f"{name}_R=1",inferred=True)
    Aux_nodes.append(f"{name}_R=1 & M{N-1}=1")
    Transition(f"{name}{N-1}_A=1",f"{name}_A=1 & "+" & ".join([f"R(M{i})" for i in range(N)]))
    Aux_nodes.append(f"{name}_A=1 & "+" & ".join([f"R(M{i})" for i in range(N)]))
    Transition(f"{name}_A=1 & "+" & ".join([f"R(M{i})" for i in range(N)]),f"{name}_A=1",inferred=True)

    
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

    Transition(name+"_T=1",name+"0_T=1")
    Transition(name+"0_S=1",name+"_F=1")
    Transition(name+"0_F=1",name+"_S=1")
    Transition(name+"0_R=1",name+"_R=1")
    Transition(name+"_H=1",name+"0_H=1")
    Transition(name+"0_A=1",name+"_A=1")

# Force Success

def CreateForceSuccess(tree,name):    

    Transition(name+"_T=1",name+"0_T=1")
    Transition(name+"0_S=1",name+"_S=1")
    Transition(name+"0_F=1",name+"_S=1")
    Transition(name+"0_R=1",name+"_R=1")
    Transition(name+"_H=1",name+"0_H=1")
    Transition(name+"0_A=1",name+"_A=1")


def CreateForceFailure(tree,name):    
    Transition(name+"_T=1",name+"0_T=1")
    Transition(name+"0_S=1",name+"_F=1")
    Transition(name+"0_F=1",name+"_F=1")
    Transition(name+"0_R=1",name+"_R=1")
    Transition(name+"_H=1",name+"0_H=1")
    Transition(name+"0_A=1",name+"_A=1")

    
# Condition node

def CreateCondition(tree,name,optimization=True):
    if "prob" in tree.attrib.keys():
        branches=tree.attrib['prob'].split(",")
    else:
        branches=["1","1","0"]
    
    if "prob" in tree.attrib.keys():
        haltable=tree.attrib['haltable']
    else:
        haltable=True
    if not (branches[0]=='0' and optimization):
        Transition(name+"_T=1",name+"_S=1")
        P.node(name+"_S=1",name+"_S=1",style="filled",color='lightblue')
        variables.append(name+"_S")
        Unsumm_nodes.append(name+"_S=1")

    if not (branches[1]=='0' and optimization):
        Transition(name+"_T=1",name+"_F=1")
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
        Transition(name+"_H=1",name+"_A=1")
        
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
        Transition(name+"_T=1",name+"_S=1")
        P.node(name+"_S=1",name+"_S=1",style="filled",color='lightblue')
        variables.append(name+"_S")
        Unsumm_nodes.append(name+"_S=1")

    
    if  not ( branches[1]=='0' and optimization):
        Transition(name+"_T=1",name+"_F=1")
        P.node(name+"_F=1",name+"_F=1",style="filled",color='lightblue')
        variables.append(name+"_F")
        Unsumm_nodes.append(name+"_F=1")

    
    if  not ( branches[2]=='0' and optimization):
        P.node(name+"_R=1",name+"_R=1",style="filled",color='lightblue')
        variables.append(name+"_R")
        Unsumm_nodes.append(name+"_R=1")
        Transition(name+"_T=1",name+"_R=1")

    
    
    if (not optimization or haltable=="True"):
        # P.edge(name+"_H=1",name+"_IH=1","",style="dashed")
        Transition(name+"_H=1",name+"_A=1")
        variables.append(name+"_H")
        variables.append(name+"_A")
        # variables.append(name+"_IH")
        # Unsumm_nodes.append(name+"_IH=1")
        Unsumm_nodes.append(name+"_H=1")
        Unsumm_nodes.append(name+"_A=1")