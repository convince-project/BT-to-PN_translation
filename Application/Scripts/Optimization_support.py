from general_support import *
import numpy

root_explored=False # Flag to state that the root has been explored
root=False # Flag to state wether a nood is the root
# Second version of the algorithm to create the Execution-flow graph
def LeafMapper2(Templates,xml,parent_connections,graph=None):
    global LeafMap,explored_leafs,root_explored,root
    ptemplate=findElementbyID(Templates,xml.tag) # template of the node type
    parent_connections["ancestor"].append(parent_connections["name"])
    if ptemplate.attrib["atomic"]=="True":
            # Move to the children adjusting the temp variable which states the connection
            for i in xml: # for each children of the node
                if list(xml).index(i)<len(xml)-1: # If it is one of the internal children
                    terminal=False
                else: # If it is the last children
                    terminal=True
                # Create the name of the current node
                codex=parent_connections["name"]+str(format(list(xml).index(i),"01x"))
                # Find the type of the current node
                template=findElementbyID(Templates,i.tag)
                # Initialize the structure for the node (This structure is used in the optimized PN construction)
                temp={"name":codex,
                          "reference":parent_connections["reference"],
                          "ancestor":copy.deepcopy(parent_connections["ancestor"]),
                          "haltable":parent_connections["haltable"]}
                # Set whether the node is the terminal child of the parent
                temp["ancestor"][-1]=temp["ancestor"][-1]+","+str(terminal)


                if template.attrib['summarizable']=="True": # if the considered node is summarizable
                    LeafMapper2(Templates,i,copy.deepcopy(temp)) # Construct the element for the child
                else:
                    # print(parent_connections)
                    if not root_explored: # check whether the root has been explored
                        root_explored=True # set that the root has been explored
                        root=True # set the current node as the root
                        parent_connections["root"]=codex
                    else: # If the root node has been explored
                        root=False # the current node cannot be the root

                    if template.attrib["id"] in Execution: # If the node is an execution node is a leaf node
                        if root: # If it is the root, it will be the "origin" of the execution flow graph
                            parent_connections["reference"]=codex # set the parent reference to the root node (current node)
                        if "haltable" in i.attrib.keys():
                            if i.attrib["haltable"]=="True": # If the node is haltable
                                parent_connections["haltable"]=True # Set the parent to haltable if the node is haltable 
                                temp["haltable"]=True # look if the node is haltable
                        if "prob" in i.attrib.keys():
                            array=i.attrib["prob"].split(",")
                            prob=[]
                            sum=0
                            for j in array:
                                prob.append(float(j))
                                sum=sum+float(j)
                            temp["prob"]=numpy.array(prob)/sum
                        else:
                            if i.tag=="BtCondition":
                                temp["prob"]=numpy.array([1,1,0])/2
                            else:
                                temp["prob"]=numpy.array([1,1,1])/3
                        LeafMap.append(temp) # Append the element to the list of leaf nodes
                    else:
                        pass
                    LeafMapper2(Templates,i,copy.deepcopy(temp)) # Explore the child recursively
    else:
        new=TreeSubElement(ptemplate[1][0],xml) # Construct the tree of a non-atomic node
        LeafMapper2(Templates,new,parent_connections) # Explore the constructed tree recursively
 