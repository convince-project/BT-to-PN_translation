from PN_support import *
import general_support as gs
import numpy
jani_structure={}

def BTParser(PNMLroot,Templates,xml,reference,other={},optimization_connections=[],path_type=[],composite_parent=None):
    global counter_nodes
    counter_nodes=counter_nodes+1
    newplace=createPT(Templates,"place",reference,1)
    returnCond=findCondition(Templates,xml)
    if reference=="R": # If the node is the root initialize the transitions and marking accordingly
        newplace=modifyField(newplace,"initialMarking/value",MarkingString([1,0,0,0,0,0]),"text") # Modification of the initial marking with the first Tick
        if GlobalOptimization and not(xml.tag=="Parallel"):
            other={"passthrough":[1,0,0,0,0,0],"parent":reference}
        elif GlobalOptimization and not(xml.tag=="Parallel"):
            other={"passthrough":[1,0,0,0,0,0],"parent":""}
        else:
            pass
        other['explored_leaves']=0
        other['sequential_leaves']=[]
        other["path_type"]=[]
        other["parent_return"]=returnCond
        if not(xml.tag=="Parallel"):
            if showReset:
                if SingleToken:
                    
                    for p in range(allowed_outcome,3):
                        
                        newreset=createPT(Templates,"reset",reference,p)
                        if GlobalOptimization:
                            if returnCond==Outcomes[p]:
                                newreset=modifyField(newreset,"priority/value",str(LeafMap[-1]["explored"]+1),"text")
                            else:
                                newreset=modifyField(newreset,"priority/value",str(LeafMap[-1]["explored"]+2),"text")
                        else:
                            newreset=modifyField(newreset,"priority/value",str(len(xml)+1),"text")
                        PNMLroot.append(newreset)
                        if not(Outcomes[p]==returnCond):
                            newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"R",p),"normal",[LeafMap[-1]["explored"]+2])
                            PNMLroot.append(newarc)
                            newarc=generateArc(Templates,generate_name(reference,"R",p),generate_name(reference,"P",1),"normal",[1])
                            PNMLroot.append(newarc)
                        else:
                            newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"R",p),"normal",[LeafMap[-1]["explored"]+1])
                            PNMLroot.append(newarc)
                            newarc=generateArc(Templates,generate_name(reference,"R",p),generate_name(reference,"P",1),"normal",[1])
                            PNMLroot.append(newarc)
                else:
                    vector=[1,0,0,0,0,0]
                    for p in range(3+allowed_outcome,6):
                        newreset=createPT(Templates,"reset",reference,p)
                        if GlobalOptimization:
                            newreset=modifyField(newreset,"priority/value",str(LeafMap[-1]["explored"]+1),"text")
                        else:
                            newreset=modifyField(newreset,"priority/value",str(len(xml)+1),"text")
                        PNMLroot.append(newreset)
                        if not(Tokens[p]==returnCond):
                            temp1=copy.copy(vector)
                            temp1[p]=1
                            newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"R",p),"normal",temp1)
                            PNMLroot.append(newarc)
                            temp1=copy.copy(vector)
                            newarc=generateArc(Templates,generate_name(reference,"R",p),generate_name(reference,"P",1),"normal",temp1)
                            PNMLroot.append(newarc)
                        else:
                            temp1=copy.copy(vector)
                            if GlobalOptimization:
                                temp1[p]=1
                            else:
                                temp1[p]=len(xml)
                            newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"R",p),"normal",temp1)
                            PNMLroot.append(newarc)
                            temp1=copy.copy(vector)
                            newarc=generateArc(Templates,generate_name(reference,"R",p),generate_name(reference,"P",1),"normal",temp1)
                            PNMLroot.append(newarc)
    
    if GlobalOptimization:
        if (other['parent']==reference):
            PNMLroot.append(newplace) # Inserting the main place in the PNML
    else:
        PNMLroot.append(newplace) # Inserting the main place in the PNML
    
    if xml.tag=="Parallel":
        
        other["sequential_leaves"].append(reference)
        exploredLeaves=other["explored_leaves"]+1
        
        # Create the Tick general transition
        if GlobalOptimization:
            source=generate_name(other["parent"],"P",1) # The source is the main place of the template
            newplace=createPT(Templates,"transition",reference,1)
            PNMLroot.append(newplace) # Inserting the main place in the PNML
            target=generate_name(reference,"T",1)
            newarc=generateArc(Templates,source,target,"normal",[1,0,0,0,0,0])
            PNMLroot.append(newarc)

            for p in range(3+allowed_outcome,3+outcomes):
                newplace=createPT(Templates,"place",reference,p)
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                newplace=createPT(Templates,"transition",reference,p)
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                newarc=generateArc(Templates,generate_name(reference,"P",p),generate_name(reference,"T",p),"normal",[1,0,0,0,0,0])
                PNMLroot.append(newarc)
                newarc=generateArc(Templates,generate_name(reference,"T",p),generate_name(other["parent"],"P",1),"normal",[1,0,0,0,0,0])
                PNMLroot.append(newarc)
            pass
        else:
            source=generate_name(reference,"P",1) # The source is the main place of the template
            newplace=createPT(Templates,"transition",reference,1)
            PNMLroot.append(newplace) # Inserting the main place in the PNML
            target=generate_name(reference,"T",1)
            newarc=generateArc(Templates,source,target,"normal",[1,0,0,0,0,0])
            PNMLroot.append(newarc)
            
            if allowHalt:
                # Create the Halt general transition
                newplace=createPT(Templates,"transition",reference,2)
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                target=generate_name(reference,"T",2)
                newarc=generateArc(Templates,source,target,"normal",[1,0,0,0,0,0])
                PNMLroot.append(newarc)
            for p in range(3+allowed_outcome,3+outcomes):
                newplace=createPT(Templates,"place",reference,p)
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                newplace=createPT(Templates,"transition",reference,p)
                PNMLroot.append(newplace) # Inserting the main place in the PNML
            # Arc between the outcome p (4=Running, 5=Success, 6=Failure) place of the parallel node and the p outcome transition
            # The condition for success is that there are M success in the success places
            # The condition for failure is that there are N-M+1 failures in the failures places
            # The condition for running are the remaining (there needs to be N ticks in the place, the places needs to be cleaned after one of the transition fires)
            # Here I need a reset arc between each of the transitions Tp and the other places Pp
                newarc=generateArc(Templates,generate_name(reference,"P",p),generate_name(reference,"T",p),"normal",[1,0,0,0,0,0])
                PNMLroot.append(newarc)
                newarc=generateArc(Templates,generate_name(reference,"T",p),generate_name(reference,"P",1),"normal",[1,0,0,0,0,0])
                PNMLroot.append(newarc)
    
    # For each child prepare the connections
    for i in xml:
        temp=copy.deepcopy(other)
        temp["path_type"].append(xml.tag)
        codex=reference+str(format(list(xml).index(i),'01x'))
        child_index=list(xml).index(i)
        newcond=findCondition(Templates,i)
        
        
        if GlobalOptimization:
            if other["parent"]==reference and list(xml).index(i)==len(xml)-1:
                temp["last_branch"]=True
            elif other["parent"]==reference and list(xml).index(i)<len(xml)-1:
                temp["last_branch"]=False
            
        if i.tag in ControlFlow: # If the child is a Control Flow node
            if xml.tag=="Parallel":
                if GlobalOptimization:
                    if not (i.tag=="Parallel"):
                        temp["parent"]=codex
                        newarc=generateArc(Templates,generate_name(reference,"T",1),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                else:
                    newarc=generateArc(Templates,generate_name(reference,"T",1),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    if allowHalt: # Local optimization of the halting condition
                        newarc=generateArc(Templates,generate_name(reference,"T",2),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                    for p in range(3+allowed_outcome,3+outcomes):
                        newplace=createPT(Templates,"transition",codex,p)
                        PNMLroot.append(newplace) # Inserting the transition associated to the outcome
                        newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",p),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",p),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
            else:
                if GlobalOptimization : # In the case we have the Global Optimization
                    # we want to create the transition and the arcs at the end of a sequential series
                    # here we want to update the arcs going up and down
                    # Create the Tick transition
                    pass
                else:
                    # Create the Tick transition
                    tickTransition=createPT(Templates,"transition",codex,1,"") # create the transition for the Tick
                    tickTransition=modifyField(tickTransition,"priority/value",str(child_index+1),"text")
                    PNMLroot.append(tickTransition) # Inserting the main place in the PNML
                    # Place to Tick transition
                    vector=[1,0,0,0,0,0]
                    if child_index>0:
                        if returnCond in Tokens:
                            if Tokens[p]==returnCond:
                                vector[p]=list(xml).index(i)
                            else:
                                vector[p]=1
                    newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",1),"normal",vector)
                    PNMLroot.append(newarc)
                    # Tick to child arc
                    newarc=generateArc(Templates,generate_name(codex,"T",1),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    
                    if allowHalt:                    # Create the Tick transition
                        tickTransition=createPT(Templates,"transition",codex,2,"") # create the transition for the Tick
                        PNMLroot.append(tickTransition) # Inserting the main place in the PNML
                        # Place to Tick transition
                        newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",2),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                        # Tick to child arc
                        newarc=generateArc(Templates,generate_name(codex,"T",2),generate_name(codex,"P",1),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                    # if list(xml).index(i)==len(list(xml))-1:
                    for p in range(3+allowed_outcome,6):
                        newplace=createPT(Templates,"transition",codex,p)
                        newplace=modifyField(newplace,"priority/value",str(len(xml)),"text")
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        vector=[1,0,0,0,0,0]
                        if showReset:
                            if not(Tokens[p]==newcond):
                                newreset=createPT(Templates,"reset",codex,p)
                                PNMLroot.append(newreset)
                                temp1=copy.copy(vector)
                                temp[p]=1
                                newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"R",p),"normal",temp1)
                                PNMLroot.append(newarc)
                                temp1=copy.copy(vector)
                                newarc=generateArc(Templates,generate_name(codex,"R",p),generate_name(codex,"P",1),"normal",temp1)
                                PNMLroot.append(newarc)
                        if Tokens[p]==returnCond:
                                vector[p]=1
                        else:
                            vector[p]=len(i)
                        
                        newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",p),"normal",vector)
                        PNMLroot.append(newarc)
                        vector=[1,0,0,0,0,0]
                        vector[p]=list(xml).index(i)+1
                        newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",1),"normal",vector)
                        PNMLroot.append(newarc)
            
            temp['index']=list(xml).index(i)
            other['index']=list(xml).index(i)
            other['explored_leaves']=BTParser(PNMLroot,Templates,i,codex,other=temp,path_type=path_type)['explored_leaves']
            other["path_type"]=other["path_type"][:-1]
            exploredLeaves=other['explored_leaves']
        elif i.tag in Execution: # If the child is an Execution node
            counter_nodes=counter_nodes+1
            other['explored_leaves']=other['explored_leaves']+1     
            if xml.tag=="Parallel": # If the execution is child to a Parallel Node
                if GlobalOptimization:
                    pass
                    # Place to Tick transition
                    newplace=createPT(Templates,"place",codex,1)
                    PNMLroot.append(newplace) # Inserting the main place in the PNML
                    newarc=generateArc(Templates,generate_name(reference,"T",1),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    if allowHalt:
                        newarc=generateArc(Templates,generate_name(reference,"T",2),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                        newplace=createPT(Templates,"transition",codex,2)
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",2),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",2),generate_name(reference,"P",1),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                    for p in range(3+allowed_outcome,3+outcomes):
                        res=next((item for item in LeafMap if (codex in item['reference']) and not(i['Success']=="R")),None)
                        newplace=createPT(Templates,"transition",codex,p)
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",p),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",p),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                else:
                    newarc=generateArc(Templates,generate_name(reference,"T",1),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    # RUNNING BRANCH OF PARALLEL
                    newplace=createPT(Templates,"place",codex,1)
                    PNMLroot.append(newplace) # Inserting the main place in the PNML
                    newplace=createPT(Templates,"transition",codex,1)
                    PNMLroot.append(newplace) # Inserting the main place in the PNML
                    newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",1),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    if allowHalt:
                        newarc=generateArc(Templates,generate_name(reference,"T",2),generate_name(codex,"P",1),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                        newplace=createPT(Templates,"transition",codex,2)
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",2),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",2),generate_name(reference,"P",1),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                    for p in range(3+allowed_outcome,3+outcomes):
                        newplace=createPT(Templates,"transition",codex,1)
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        newarc=generateArc(Templates,generate_name(codex,"T",1),generate_name(reference,"P",p),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
            else: # If the node is child to a Sequential node
                other["sequential_leaves"].append(codex)
                newplace=createPT(Templates,"transition",codex,1)
                if GlobalOptimization:
                    newplace=modifyField(newplace,"priority/value",str(other['explored_leaves']),"text")
                else:    
                    newplace=modifyField(newplace,"priority/value",str(child_index+1),"text")
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                vector=[1,0,0,0,0,0]
                if child_index>0:
                    if returnCond in Tokens:
                        vector[Tokens.index(returnCond)]=1
                newplace=createPT(Templates,"place",codex,2)
                if SingleToken:
                    newplace=modifyField(newplace,"initialMarking/value",MarkingString([0]),"text") # Modification of the initial marking with the first Tick
                PNMLroot.append(newplace) # Inserting the main place in the PNML
                if GlobalOptimization:
                    if SingleToken:
                        res=next((item for item in LeafMap if (codex in item['reference'])),None)
                        # Place to Tick transition
                        newarc=generateArc(Templates,generate_name(other['parent'],"P",1),generate_name(codex,"T",1),"normal",[other['explored_leaves']])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",1),generate_name(codex,"P",2),"normal",[1])
                        PNMLroot.append(newarc)
                    else:
                        res=next((item for item in LeafMap if (codex in item['reference'])),None)
                        # Place to Tick transition
                        newarc=generateArc(Templates,generate_name(other['parent'],"P",1),generate_name(codex,"T",1),"normal",[1,0,other['explored_leaves']-1,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",1),generate_name(codex,"P",2),"normal",[1,0,0,0,0,0])
                        PNMLroot.append(newarc)
                    
                else:
                    
                    newarc=generateArc(Templates,generate_name(codex,"T",1),generate_name(codex,"P",2),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",1),"normal",vector)
                    PNMLroot.append(newarc)
                    if allowHalt and i.tag=="BtAction":
                        # EXECUTION TRANSITION
                        newplace=createPT(Templates,"transition",codex,2)
                        PNMLroot.append(newplace) # Inserting the main place in the PNML
                        newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",2),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                        newarc=generateArc(Templates,generate_name(codex,"T",2),generate_name(reference,"P",1),"normal",[0,1,0,0,0,0])
                        PNMLroot.append(newarc)
                # EXECUTION TRANSITION
                if i.tag=="BtCondition":
                    allowed_outcome1=1
                    outcomes1=3
                else:
                    allowed_outcome1=allowed_outcome
                    outcomes1=outcomes
                for p in range(3+allowed_outcome1,3+outcomes1):
                    
                    # Success    
                    newarc=generateArc(Templates,generate_name(codex,"P",2),generate_name(codex,"T",p),"normal",[1,0,0,0,0,0])
                    PNMLroot.append(newarc)
                    newplace=createPT(Templates,"transition",codex,p)
                    PNMLroot.append(newplace) # Inserting the main place in the PNML
                    vector=[1,0,0,0,0,0]
                    if GlobalOptimization:
                        if SingleToken:
                            if res[Outcomes[p-3]]==other['parent']:
                                if temp["last_branch"]:
                                    if Outcomes[p-3]==other["parent_return"]:
                                        vector=[LeafMap[-1]["explored"]+1]
                                    else:
                                        vector=[LeafMap[-1]["explored"]+2]
                                else:
                                    vector=[LeafMap[-1]["explored"]+2]
                            else:
                                res1=next((item for item in LeafMap if (res[Outcomes[p-3]] in item['reference'])),temp)
                                vector=[res1['explored']]                            
                            if xml.tag=="Parallel":
                                newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",p),"normal",vector)
                                PNMLroot.append(newarc)
                            else:
                                newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(other['parent'],"P",1),"normal",vector)
                                PNMLroot.append(newarc)
                        else:
                            if res[Tokens[p]]==other['parent']:
                                vector[p]=1
                            else:
                                res1=next((item for item in LeafMap if (res[Tokens[p]] in item['reference'])),temp)
                                vector[p]=1
                                vector[2]=res1['explored']-1
                            
                            if xml.tag=="Parallel":
                                newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",p),"normal",vector)
                                PNMLroot.append(newarc)
                            else:
                                newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(other['parent'],"P",1),"normal",vector)
                                PNMLroot.append(newarc)
                    else:
                        if Tokens[p]==returnCond:
                            if list(xml).index(i)==len(xml)-1:
                                vector[p]=list(xml).index(i)+1
                            else:
                                vector[p]=list(xml).index(i)+1
                        else:
                            vector[p]=1
                        if xml.tag=="Parallel":
                            newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",p),"normal",vector)
                            PNMLroot.append(newarc)
                        else:
                            newarc=generateArc(Templates,generate_name(codex,"T",p),generate_name(reference,"P",1),"normal",vector)
                            PNMLroot.append(newarc)
    exploredLeaves=other["explored_leaves"]
    return {"modifiedRoot":PNMLroot[0],"explored_leaves":exploredLeaves}



# Second version of the parser to Petri Nets
def BTParser2(PNMLroot,Templates,xml,reference,other={},path_type=[],extra=None):
    global counter_nodes,jani_structure
    
    ptemplate=findElementbyID(Templates,xml.tag) # template of the node type
    if ptemplate.attrib["atomic"]=="True":
        counter_nodes=counter_nodes+1
        newplace=createPT(Templates,"place",reference,1) # Main place for the template
        if reference=="R": # If the node is the root initialize the transitions and marking accordingly
            jani_vector=[1,0,0,0,0,0]
            for i in Tokens:
                # Creation of the JANI place by creating the variables for each quantity
                variable={'initial-value':jani_vector[Tokens.index(i)],'name':reference+str(Tags[Tokens.index(i)]),'type':'int'}
                gs.jani_structure['variables'].append(variable)
                variable={'initial-value':0,'name':"O"+str(Tags[Tokens.index(i)]),'type':'int'}
                gs.jani_structure['variables'].append(variable)
            newplace=modifyField(newplace,"initialMarking/value",MarkingString(jani_vector),"text") # Modification of the initial marking with the first Tick
            if GlobalOptimization:
                other={"passthrough":[1,0,0,0,0,0],"parent":reference}
            other['explored_leaves']=0
            other['sequential_leaves']=[]
            other["path_type"]=[]                
            for p in range(3):
                extra.edge(reference,"O",label="O"+str(p),color="blue")
                vector1=parseVector(ptemplate[1][p+2].attrib["value"],{"N":len(xml)})
                vector3=[0,0,0,0,0,0]
                vector3[(p+1)%3+3]=1
                create_final_assignment(vector1,vector3,reference,"O",gs.jani_structure)
                extra.edge("O",reference,label=str(vector3)+"->[1, 0, 0, 0, 0, 0]",color="red")
                vector2=parseVector(ptemplate[1][0].attrib["value"],{"N":len(xml)})
                create_final_assignment(vector3,vector2,"O",reference,gs.jani_structure)  
                    
        else:
            jani_vector=[0,0,0,0,0,0]
            
            for i in range(len(Tokens)):
                # Creation of the JANI place by creating the variables for each quantity
                variable={'initial-value':jani_vector[i],'name':reference+str(Tags[i]),'type':'int'}
                gs.jani_structure['variables'].append(variable)
            # Creating the six arcs connecting to the parent transitions
            for j in range(2,6):
                out_vector=parseVector(ptemplate[1][j].attrib["value"],{"N":len(xml)})
                if j<3:
                    in_vector=parseVector(ptemplate[1][1].attrib["value"],{"N":len(xml)})
                else:
                    in_vector=parseVector(ptemplate[1][0].attrib["value"],{"N":len(xml)})
                if not (sum(out_vector)==0 or sum(in_vector)==0):
                    newarc=generateArc(Templates,generate_name(reference,"T",j+1),generate_name(reference,"P",1),"normal",out_vector)
                    PNMLroot.append(newarc)
                    newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"T",j+1),"normal",in_vector)
                    PNMLroot.append(newarc)
                 
        PNMLroot.append(newplace)
        # Children amministration
        for i in xml: # for each child of the node
            
            temp=copy.deepcopy(other)
            temp["path_type"].append(xml.tag)
            codex=reference+str(format(list(xml).index(i),'01x'))
            child_index=list(xml).index(i)
            template=findElementbyID(Templates,i.tag)  # template of the node type
            if template.attrib["atomic"]=="True" or i.tag in Execution:
                if GlobalOptimization: # If the GlobalOptimization is true
                    if other["parent"]==reference and list(xml).index(i)==len(xml)-1:
                        temp["last_branch"]=True
                    elif other["parent"]==reference and list(xml).index(i)<len(xml)-1:
                        temp["last_branch"]=False
                
                if len(list(ptemplate[1]))>13: # Creating the arcs for reactive nodes to send the result after having the nodes haltes
                        for p in range(3):
                            if list(xml).index(i)<len(xml)-1: # if we are not in the final node of a reactive node
                                vector1=parseVector(ptemplate[1][p+12].attrib["value"],{"N":len(i),"i":list(xml).index(i)})
                                if vector1[0]==0: # if we need to halt the child
                                    te=findElementbyID(Templates,xml[list(xml).index(i)+1].tag)
                                    if te.attrib["atomic"]=="True":
                                        codex1=reference+str(list(xml).index(i)+1)
                                        vector2=parseVector(te[1][1].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                                        construct_halt_assignment(vector1,vector2,reference,codex1,gs.jani_structure)
                                    else:
                                        te1=findElementbyID(Templates,te[1][0].tag)
                                        codex1=reference+str(list(xml).index(i)+1)
                                        vector2=parseVector(te1[1][0].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                                        construct_halt_assignment(vector1,vector2,reference,codex1,gs.jani_structure)
                if i.tag in ControlFlow:  # Case for the child being a control flow node
                    
                    if GlobalOptimization:
                        pass
                    else:      
                        for j in range(6):
                            vector2=parseVector(ptemplate[1][j+6].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                            vector1=parseVector(template[1][j].attrib["value"],{"N":len(i),"i":list(xml).index(i)})
                            if "memory" in ptemplate[1][j+6].attrib.keys():
                                memory=ptemplate[1][j+6].attrib["memory"]
                            else:
                                memory=False
                            if sum(vector1)>0 and sum(vector2)>0:
                                if j< 2:
                                    

                                    if j>0:
                                        construct_halt_assignment(vector2,vector1,reference,codex,gs.jani_structure)
                                    else:
                                        if "memory" in template[1][j].attrib.keys():                                        
                                            memory=template[1][j].attrib["memory"]
                                        else:
                                            memory=False
                                        construct_assignment(vector2,vector1,reference,codex,gs.jani_structure,memory=memory)
                                    extra.edge(reference,codex,label=str(vector2)+"->"+str(vector1),color="red")
                                else:
                                    if j<5:
                                        if "memory" in template[1][j].attrib.keys():                                        
                                            memory=template[1][j].attrib["memory"]
                                        else:
                                            memory=False
                                        construct_assignment(vector1,vector2,codex,reference,gs.jani_structure,memory=memory)
                                    else:
                                        construct_halt_assignment(vector1,vector2,codex,reference,gs.jani_structure)
                                    extra.edge(codex,reference,label=str(vector2)+"->"+str(vector1),color="blue")
                                    
                            # Creating the six transition connecting to each child
                            newplace=createPT(Templates,"transition",codex,j+1)
                            newplace=modifyField(newplace,"priority/value",str(child_index+1),"text")
                            PNMLroot.append(newplace)
                            # Create the arcs connecting the main place to the transitions of each child
                            vector=parseVector(ptemplate[1][j+6].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                            if sum(vector)>0:
                                if template[1][j].tag[1]=="I": # Arcs connecting the children output transition to the node main place
                                    newarc=generateArc(Templates,generate_name(codex,"T",j+1),generate_name(reference,"P",1),"normal",vector)
                                else: # Arcs connecting the node main place to the children input transition
                                    newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",j+1),"normal",vector)
                                PNMLroot.append(newarc)

                    temp['index']=list(xml).index(i)
                    other['index']=list(xml).index(i)
                    
                    other['explored_leaves']=BTParser2(PNMLroot,Templates,i,codex,other=temp,path_type=path_type,extra=extra)
                    
                
                elif i.tag in Execution: # Case for the child being an Execution node
                    counter_nodes=counter_nodes+1
                    temp_vector=[]
                    memory_vector=[]
                    
                    # Generate the connection between the execution node and the parent node
                    for j in range(6):
                        vector=parseVector(template[1][j].attrib["value"],{})
                        if "memory" in ptemplate[1][j+6].attrib.keys():
                            memory=ptemplate[1][j+6].attrib["memory"]
                        else:
                            memory=False
                        enabled=int(template[1][j].attrib["enabled"])
                        if enabled:
                            # Creating the six transition connecting to each child
                            newplace=createPT(Templates,"transition",codex,j+1)
                            newplace=modifyField(newplace,"priority/value",str(child_index+1),"text")
                            PNMLroot.append(newplace)
                            pvector=parseVector(ptemplate[1][j+6].attrib["value"],{"i":list(xml).index(i)})
                            k=0
                            if sum(pvector)>0:
                                k+=1
                                # Create the arcs connecting the child place to the transitions of the parent
                                if template[1][j].tag[1]=="I":
                                    newarc=generateArc(Templates,generate_name(codex,"T",j+1),generate_name(reference,"P",1),"normal",pvector)
                                else:
                                    if simplified:
                                        newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",j+1),"normal",pvector)
                                    else:
                                        newarc=generateArc(Templates,generate_name(reference,"I",1),generate_name(codex,"T",j+1),"normal",pvector)
                                PNMLroot.append(newarc)
                            
                            if sum(vector)>0:
                                k+=1
                                # Create the arcs connecting the transitions of the parent to the main place of the parent
                                if template[1][j].tag[1]=="O":
                                    newarc=generateArc(Templates,generate_name(codex,"T",j+1),generate_name(codex,"P",1),"normal",vector)
                                else:
                                    if simplified and j>=5:
                                        vector=parseVector("0,1,0,0,0,0",{"i":list(xml).index(i)})
                                    elif simplified and j<5:
                                        vector=parseVector("1,0,0,0,0,0",{"i":list(xml).index(i)})
                                    else:
                                        vector=parseVector(vector,{"i":list(xml).index(i)})
                                    
                                    newarc=generateArc(Templates,generate_name(codex,"P",1),generate_name(codex,"T",j+1),"normal",vector)
                                PNMLroot.append(newarc)
                            if k==2:
                                if j< 2:
                                    if j<1:
                                        construct_assignment(pvector,vector,reference,codex,gs.jani_structure,memory=memory)
                                    else:
                                        construct_halt_assignment(pvector,vector,reference,codex,gs.jani_structure,memory=memory)
                                    extra.edge(reference,codex,label=str(pvector)+"->"+str(vector),color="red")
                                else:
                                    if i.tag=="BtCondition":
                                        if j<5:
                                            probability=[.5,.5]
                                            temp_vector.append(pvector)
                                            memory_vector.append(memory)
                                            if len(temp_vector)==2:
                                                construct_prob_assignment(vector,temp_vector,codex,reference,gs.jani_structure,probability=probability,memory=memory_vector)
                                            extra.edge(codex,reference,label=str(vector)+"->"+str(pvector)+","+str(probability),color="blue")
                                        else:
                                            temp_vector=[]
                                            probability=1
                                            temp_vector.append(pvector)
                                            construct_halt_assignment(vector,temp_vector[0],codex,reference,gs.jani_structure)
                                            extra.edge(codex,reference,label=str(vector)+"->"+str(temp_vector[0])+","+str(probability),color="blue")                             
                                    else:
                                        if j<5:
                                            if "prob" in i.attrib.keys():
                                                if j==2:
                                                    array=i.attrib["prob"].split(",")
                                                    prob=[]
                                                    sum1=0
                                                    for p in array:
                                                        prob.append(float(p))
                                                        sum1=sum1+float(p)
                                                    prob_vector=numpy.array(prob)/sum1
                                                probability=prob_vector
                                            else:
                                                probability=[1/3,1/3,1/3]
                                            temp_vector.append(pvector)
                                            memory_vector.append(memory)
                                            if len(temp_vector)==3:
                                                construct_prob_assignment(vector,temp_vector,codex,reference,gs.jani_structure,probability=probability,memory=memory_vector)
                                            extra.edge(codex,reference,label=str(vector)+"->"+str(pvector)+","+str(probability),color="blue")
                                        else:
                                            temp_vector=[]
                                            probability=1
                                            temp_vector.append(pvector)
                                            construct_halt_assignment(vector,temp_vector[0],codex,reference,gs.jani_structure)
                                            extra.edge(codex,reference,label=str(vector)+"->"+str(temp_vector[0])+","+str(probability))
                                                                            
                    # Create the internal main place for the Execution node
                    newplace=createPT(Templates,"place",codex,1) # Main place for the template
                    PNMLroot.append(newplace)
                    for k in Tokens:
                        jani_vector=[0,0,0,0,0,0]
                        variable={'initial-value':jani_vector[Tokens.index(k)],'name':codex+str(Tags[Tokens.index(k)]),'type':'int'}
                        gs.jani_structure['variables'].append(variable)
                    if not simplified: # If not simplified the internal structure of the Execution node must be expanded

                        # Create the Tick and Halt transition inside the execution node
                    
                        newplace=createPT(Templates,"transition",codex,1) # Tick transition for the template
                        PNMLroot.append(newplace)
                        

                        newplace=createPT(Templates,"transition",codex,2) # Halt transition for the template
                        PNMLroot.append(newplace)


                        # Create the Interface
                        newplace=createPT(Templates,"interface",codex,1) # Interface
                        PNMLroot.append(newplace)
                    
                        # Create the arcs between all elements
                    
                        # Arc moving Tick from place to transition
                        newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"T",1),"normal","1,0,0,0,0,0")
                        PNMLroot.append(newarc)

                        # Arc moving Halt from place to transition
                        newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(reference,"T",2),"normal","0,1,0,0,0,0")
                        PNMLroot.append(newarc)

                        # Arc moving Tick from transition to interface
                        newarc=generateArc(Templates,generate_name(reference,"T",1),generate_name(reference,"I",1),"normal","1,0,0,0,0,0")
                        PNMLroot.append(newarc)

                        # Arc moving Halt from transition to interface
                        newarc=generateArc(Templates,generate_name(reference,"T",2),generate_name(reference,"I",1),"normal","0,1,0,0,0,0")
                        PNMLroot.append(newarc)
                    else:
                        pass
                else:
                    pass     
            else:
                if len(list(ptemplate[1]))>13: # Creating the arcs for reactive nodes to send the result after having the nodes haltes
                        for p in range(3):
                            if list(xml).index(i)<len(xml)-1: # if we are not in the final node of a reactive node
                                vector1=parseVector(ptemplate[1][p+12].attrib["value"],{"N":len(i),"i":list(xml).index(i)})
                                if vector1[0]==0: # if we need to halt the child
                                    te=findElementbyID(Templates,xml[list(xml).index(i)+1].tag)
                                    if te.attrib["atomic"]=="True":
                                        codex1=reference+str(list(xml).index(i)+1)
                                        vector2=parseVector(te[1][1].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                                        construct_halt_assignment(vector1,vector2,reference,codex1,gs.jani_structure)
                                    else:
                                        te1=findElementbyID(Templates,te[1][0].tag)
                                        codex1=reference+str(list(xml).index(i)+1)
                                        vector2=parseVector(te1[1][0].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                                        construct_halt_assignment(vector1,vector2,reference,codex1,gs.jani_structure)
                if i.tag in ControlFlow:  # Case for the child being a control flow node
                    new=TreeSubElement(template[1][0],i)
                    template=findElementbyID(Templates,new.tag) # template of the node type
                    if GlobalOptimization:
                        pass
                    else:      
                        for j in range(6):
                            vector2=parseVector(ptemplate[1][j+6].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                            vector1=parseVector(template[1][j].attrib["value"],{"N":len(i),"i":list(xml).index(i)})
                            if "memory" in ptemplate[1][j+6].attrib.keys():
                                memory=ptemplate[1][j+6].attrib["memory"]
                            else:
                                memory=False
                            if sum(vector1)>0 and sum(vector2)>0:
                                if j< 2:
                                    

                                    if j>0:
                                        construct_halt_assignment(vector2,vector1,reference,codex,gs.jani_structure)
                                    else:
                                        if "memory" in template[1][j].attrib.keys():                                        
                                            memory=template[1][j].attrib["memory"]
                                        else:
                                            memory=False
                                        construct_assignment(vector2,vector1,reference,codex,gs.jani_structure,memory=memory)
                                    extra.edge(reference,codex,label=str(vector2)+"->"+str(vector1),color="red")
                                else:
                                    if j<5:
                                        if "memory" in template[1][j].attrib.keys():                                        
                                            memory=template[1][j].attrib["memory"]
                                        else:
                                            memory=False
                                        construct_assignment(vector1,vector2,codex,reference,gs.jani_structure,memory=memory)
                                    else:
                                        construct_halt_assignment(vector1,vector2,codex,reference,gs.jani_structure)
                                    extra.edge(codex,reference,label=str(vector2)+"->"+str(vector1),color="blue")
                                    
                            # Creating the six transition connecting to each child
                            newplace=createPT(Templates,"transition",codex,j+1)
                            newplace=modifyField(newplace,"priority/value",str(child_index+1),"text")
                            PNMLroot.append(newplace)
                            # Create the arcs connecting the main place to the transitions of each child
                            vector=parseVector(ptemplate[1][j+6].attrib["value"],{"N":len(xml),"i":list(xml).index(i)})
                            if sum(vector)>0:
                                if template[1][j].tag[1]=="I": # Arcs connecting the children output transition to the node main place
                                    newarc=generateArc(Templates,generate_name(codex,"T",j+1),generate_name(reference,"P",1),"normal",vector)
                                else: # Arcs connecting the node main place to the children input transition
                                    newarc=generateArc(Templates,generate_name(reference,"P",1),generate_name(codex,"T",j+1),"normal",vector)
                                PNMLroot.append(newarc)
                
                temp['index']=list(xml).index(i)
                other['index']=list(xml).index(i)
                other['explored_leaves']=BTParser2(PNMLroot,Templates,new,codex,other=temp,path_type=path_type,extra=extra)

                
        exploredLeaves=other["explored_leaves"]
        return {"modifiedRoot":PNMLroot[0],"explored_leaves":exploredLeaves}
    else: # When we have not atomic nodes (nodes that can be structured as a composition of atomic nodes)
        new=TreeSubElement(ptemplate[1][0],xml)
        if GlobalOptimization:
                other={"passthrough":[1,0,0,0,0,0],"parent":reference}
        other['explored_leaves']=0
        other['sequential_leaves']=[]
        other["path_type"]=[]
        other['explored_leaves']=BTParser2(PNMLroot,Templates,new,reference,extra=extra)
        exploredLeaves=other["explored_leaves"]
        return {"modifiedRoot":PNMLroot[0],"explored_leaves":exploredLeaves}
            
                
