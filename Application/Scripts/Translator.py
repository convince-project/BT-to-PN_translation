from PN_parser import *
from Optimization_support import *
from tkinter.filedialog import askopenfilename
from typing import Tuple, List, Iterable
from pydot import Dot, graph_from_dot_data, Edge
from graphviz.graphs import BaseGraph
from graphviz import Source
import networkx as nx
import PN_support
import re

import matplotlib.pyplot as plt

script_path = os.path.abspath(__file__)
script_path=os.path.dirname(os.path.dirname(script_path))

from nodes_formalization import *

def parseBT(tree,name,optimization_=False):
    node_counter=0
    for i in tree:
        if not name=="":
            tag=name+str(list(tree).index(i))
        else:
            tag="R"
            P.node("R_T=1","R_T=1",style="filled",color='lightblue')
            Unsumm_nodes.append("R_T=1")
            P.node("R_H=1","R_H=1",style="filled",color='lightblue')
            Unsumm_nodes.append("R_H=1")
            P.node("R_S=1","R_S=1",style="filled",color='lightblue')
            Unsumm_nodes.append("R_S=1")
            P.node("R_F=1","R_F=1",style="filled",color='lightblue')
            Unsumm_nodes.append("R_F=1")
            P.node("R_R=1","R_R=1",style="filled",color='lightblue')
            Unsumm_nodes.append("R_R=1")
            P.node("R_A=1","R_A=1",style="filled",color='lightblue')
            Transition("R_A=1","R_T=1")
            Transition("R_S=1","R_T=1")
            Transition("R_F=1","R_T=1")
            Transition("R_R=1","R_T=1")

        parseBT(i,tag,optimization_=optimization_)

    if len(list(tree))==0:
        if tree.tag=="BtCondition":
            CreateCondition(tree,name,optimization=optimization_)
        else:
            CreateAction(tree,name,optimization=optimization_)
    else:
        
        if tree.tag=="ReactiveSequence":
                CreateReactiveNode(tree,name,"S",optimization=optimization_)
        elif tree.tag=="ReactiveFallback":
                CreateReactiveNode(tree,name,"F",optimization=optimization_)
        elif tree.tag=="Sequence":
            CreateMemoryNode(tree,name,"S")
        elif tree.tag=="Fallback":
            CreateMemoryNode(tree,name,"F")
        elif tree.tag=="Inverter":
            CreateInverter(tree,name)
        elif tree.tag=="Parallel":
            CreateParallel(tree,name)
        elif tree.tag=="Switch2":
            CreateSwitch2(tree,name)
        elif tree.tag=="ForceSuccess":
            CreateForceSuccess(tree,name)
        elif tree.tag=="RetryUntilSuccessful":
            if "num_attempts" in tree.attrib.keys():
                number_of_iterations=tree.attrib["num_attempts"]
            elif "number_of_retries" in tree.attrib.keys():
                number_of_iterations=tree.attrib["number_of_retries"]
            else:
                pass
            CreateRetryUntilSuccessful(tree,name,number_of_iterations)
        elif tree.tag=="BehaviorTree":
            pass
        else:
            CreateAction(tree,name,optimization=optimization_)
    node_counter+=1        
    
    return

def floodFill(G,node,Q,trace=[],contract=False):
    out_arcs=G.out_edges(node)
    for i in out_arcs: # For the arcs going out of the node
        if i[1].split("\"")[1] in Unsumm_nodes: # if the node is important
            if trace==[]: # If the current trace is empty
                if not Q.has_edge(i[0],i[1]): #If the current arc is not in the temporary graph
                    F.edge(i[0].split("\"")[1],i[1].split("\"")[1]) # Put the current edge in the final graph
                    Q.add_edge(i[0],i[1]) # Add the edge to the temporary graph
            else:
                temp=copy.deepcopy(trace)
                temp.append(i[1].split("\"")[1])
                idx1=0
                idx2=1
                for k in range(len(temp)-1): # reading through the temp trace
                    if (temp[idx1] in Unsumm_nodes or temp[idx1] in Aux_nodes) and (temp[idx2] in Unsumm_nodes or temp[idx2] in Aux_nodes):  # if two elements of the temp trace are both unssumarizable  
                        if not Q.has_edge(temp[idx1],temp[idx2]): #If the current arc is not in the temporary graph
                            F.edge(temp[idx1],temp[idx2]) # Put the current edge in the final graph
                            Q.add_edge(temp[idx1],temp[idx2]) # Add the edge to the temporary graph
                        idx1=idx2
                        idx2=idx1+1
                    else:
                        idx2+=1
                        
        else:
            temp_trace=copy.copy(trace)
            if temp_trace==[]:
                temp_trace.append(i[0].split("\"")[1])
            temp_trace.append(i[1].split("\"")[1])
            floodFill(G,i[1],Q,trace=temp_trace)

class Node:
    label=""
    attributes=None
    def __init__(self,text):
        self.attributes=[]
        parsed1=text.split("[")
        if len(parsed1)>1:
            self.label=text.split("[")[0]
            temp=text.split("[")[1][:-1].split(" ")
            for i in temp:
                if not len(i.split("="))==1:
                    if not i.split("=")[0]=="label":
                        self.attributes.append((i.split("=")[0],i.split("=")[1]))
        else:
            self.label=text
    
    def to_text(self,graph):
        name=self.label.split("\"")[1]
        attributes=dict(self.attributes)
        graph.node(name,_attributes=attributes)
        
        return graph

class Edge:
    label=""
    attributes=None
    def __init__(self,text,label=None,attributes=None):
        # print(attributes)
        self.attributes=[]
        if attributes:
            self.attributes=attributes
            self.label=text
        else:
            parsed1=text.split("[")
            if len(parsed1)>1:
                self.label=text.split("[")[0][:-1]
                temp=text.split("[")[1][:-1].split(" ")
                for i in temp:
                    if not len(i.split("="))==1:
                        if not i.split("=")[0]=="label":
                            self.attributes.append((i.split("=")[0],i.split("=")[1]))
                        else:
                            if not i.split("=")[1]=="\"\"":
                                self.attributes.append((i.split("=")[0],i.split("=")[1]))
            else:
                self.label=text

    def to_text(self,graph):
        ends=self.label.split("->")
        # print(self.label)
        attributes=dict(self.attributes)
        graph.edge(ends[0].split("\"")[1],ends[1].split("\"")[1],_attributes=attributes)
        
        return graph

class Graph:
    nodes=None
    edges=None
    edge_list=None
    edge_dict=None
    variables_list=None
    PN_places=None
    PN_transitions=None

    text_places=[]
    text_transitions=[]
    text_arcs=[]
    text_inhibitor=[]
    text=""

    def __init__(self,graph):
        self.text=graph.source
        self.nodes=[]
        self.edges=[]
        self.edge_list=[]
        self.edge_dict={}
        self.variables_list=[]
        self.PN_places=[]
        self.PN_transitions=[]
        self.elements=self.reparse(graph)
        self.extract_elements()
        
    def print_nodes(self):
        for i in self.nodes:
            print(i.label,i.attributes)
    
    def delete_arc(self,text):
        for i in self.edges:
            if i.label==text:
                self.edges.remove(i)

                # print((text.split("->")[0],text.split(" -> ")[1]))

                self.edge_list.remove((text.split("->")[0],text.split("->")[1]))
                break
    
    def delete_variable(self,text):
        for i in self.edges:
            if text in i.label:
                self.edges.remove(i)
        for i in self.nodes:
            if text in i.label:
                self.nodes.remove(i)

    def add_arc(self,text,attributes=[]):
        temp_edge=Edge(text,attributes=attributes)
        self.edge_dict[temp_edge.label]=temp_edge
        self.edges.append(temp_edge)
        x=temp_edge.label.split("->")[0]
        y=temp_edge.label.split("->")[1]
        self.edge_list.append((x,y))

    def modify_nodes(self,attributes,lists=[]):
        if len(lists)>0:
            for i in self.nodes:
                i.attributes=lists
        else:
            for i in self.nodes:
                i.attributes+=attributes

    def modify_arcs(self,attributes,lists):
        if len(lists)>0:
            pass
        else:
            for i in self.nodes:
                i.attributes+=attributes

    def extract_elements(self):
        for i in self.elements:
            if "->" in i:
                temp_edge=Edge(i)
                self.edges.append(temp_edge)
                self.edge_dict[temp_edge.label]=temp_edge
                x=temp_edge.label.split("->")[0]
                y=temp_edge.label.split("->")[1]
                label_x=x.split("\"")[1]
                label_y=y.split("\"")[1]
                if "&" in label_x:
                    for k in label_y.split(" & "):
                        part=k
                        if not part in self.variables_list:
                            self.variables_list.append(part)
                else:
                    if not label_x in self.variables_list:
                        self.variables_list.append(label_x)
                
                if "&" in label_y:
                    for k in label_y.split(" & "):
                        part=k
                        if not part in self.variables_list:
                            self.variables_list.append(part)
                    
                else:
                    if not label_y in self.variables_list:
                        self.variables_list.append(label_y)

                self.edge_list.append((x,y))
            else:
                temp_node=Node(i)
                self.nodes.append(temp_node)

    def construct_graph(self):
        temp=Digraph(format='gv')
        temp.engine="dot"
        for i in self.edges:
            temp=i.to_text(temp)
        for i in self.nodes:
            temp=i.to_text(temp)
        return temp
    
    def construct_PN(self,contracted=False):
        temp=Digraph(format='gv')
        temp.engine="dot"
        arrowstyle="odot"
        for i in self.edge_list:
            
            if "R_T" in i[0] or "R_T" in i[1]:
                pass
                # print(i)

                # print(i[0]+"->"+i[1] in Inf_arcs,self.edge_dict[i[0]+"->"+i[1]].attributes)
            blocker=0
            for j in self.edge_dict[i[0]+"->"+i[1]].attributes:
                if j[0]=="color":
                    blocker=1
            if blocker==1:
                continue
            inputs=i[0].split("\"")[1]
            outputs=i[1].split("\"")[1]

            

            # print(inputs,"-",outputs)
            
            if not ("I" in inputs or "I" in outputs):
                if "label" in dict(self.edge_dict[i[0]+"->"+i[1]].attributes).keys():
                    # print(self.edge_dict[i[0]+"->"+i[1]].attributes)
                    temp.node(inputs+"->"+outputs,"2",xlabel="2", style = 'filled', color = 'black', shape = "box", width="0.7", height="0.14",fontcolor='white',fontname="arial bold")
                else:
                    temp.node(inputs+"->"+outputs,"",xlabel="", style = 'filled', color = 'black', shape = "box", width="0.7", height="0.14",fontcolor='white',fontname="arial bold")
                self.PN_transitions.append(inputs+"->"+outputs)
            
            for j in inputs.split(" & "):
                # printTree(rank,0)
                list1=re.split(r'(>=|=|\+=|<)',j)
                if "+" in list1[2]:
                    inscription=list1[2].split("+")[1]
                else:
                    inscription=list1[2]

                if "I" in list1[0]:
                    
                    temp1=i[1].split("\"")[1]
                    list2=re.split(r'(>=|=|\+=|<)',temp1)
                    if not contracted:
                        if "not" in list1[0]:
                             temp.edge(list1[0].split(" ")[1],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        elif not ">=" in list1[1] and inscription=="0":
                            temp.edge(list1[0],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        else:
                            temp.edge(list1[0],list2[0],label=inscription)
                        if ">=" in list1[1]:
                            temp.edge(inputs+"->"+outputs,list2[0],arrowhead="odiamond")

                        temp.node(list1[0],"",xlabel="1", style = 'filled', color = 'black', shape = "square",fontcolor='white',fillcolor="white",fontname="arial bold")
                    else: # If I need to connect the input to the output without interface
                        temp_string=list1[0].split("I")[0]+list1[0].split("I")[1]
                        if "not" in list1[0]:
                             temp.edge(list1[0].split(" ")[1],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        elif not ">=" in list1[1] and inscription=="0":
                            temp.edge(list1[0],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        else:
                            temp.node(temp_string+"->"+list2[0],"",xlabel="", style = 'filled', color = 'black', shape = "box", width="0.7", height="0.14",fontcolor='white',fontname="arial bold")
                            temp.edge(temp_string,temp_string+"->"+list2[0],label=inscription)
                            temp.edge(temp_string+"->"+list2[0],list2[0],label=inscription)
                        if ">=" in list1[1] and not "not" in list1[0]:
                            if "not" in list1[0]:
                                output=list1[0].split(" ")[1]
                            else:
                                output=list1[0]
                            temp.edge(temp_string,output,arrowhead="odiamond")
                else:
                    if not "I" in inputs+"->"+outputs:
                        if "not" in list1[0]:
                             temp.edge(list1[0].split(" ")[1],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        elif not ">=" in list1[1] and inscription=="0":
                            temp.edge(list1[0],inputs+"->"+outputs,label=inscription,arrowhead=arrowstyle)
                        else:
                            temp.edge(list1[0],inputs+"->"+outputs,label=inscription)
                        
                        
                        if ">=" in list1[1] and not "not" in list1[0]:
                            if "not" in list1[0]:
                                output=list1[0].split(" ")[1]
                            else:
                                output=list1[0]
                            temp.edge(inputs+"->"+outputs,output,arrowhead="odiamond")

                    if "not" in list1[0]:
                        label=list1[0].split("not ")[1]
                    else:
                        label=list1[0]
                    temp.node(label,label,xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")
                    if not label in self.PN_places:
                        self.PN_places.append(label)
            
            for j in outputs.split(" & "):
                # printTree(rank,0)
                list1=re.split(r'(>=|=|\+=)',j)
                if "+" in list1[2]:
                    inscription=list1[2].split("+")[1]
                else:
                    inscription=list1[2]

                if "I" in list1[0]:
                    if not contracted:
                        temp1=i[0].split("\"")[1]
                        list2=re.split(r'(>=|=|\+=|<)',temp1)
                        if "not" in list1[0] or inscription=="0":
                            if "not" in list1[0]:
                                output=list1[0].split(" ")[1]
                            else:
                                output=list1[0]
                            temp.edge(list2[0],output,label=inscription,arrowhead=arrowstyle)
                        else:
                            if "not" in list1[0]:
                                output=list1[0].split(" ")[1]
                            else:
                                output=list1[0]
                            temp.edge(list2[0],output,label=inscription)
                        temp.node(output,"",xlabel="1", style = 'filled', color = 'black', shape = "square",fontcolor='white',fillcolor="white",fontname="arial bold")
                        
                    
                else: 
                    if not "I" in inputs+"->"+outputs:
                        if "not" in list1[0] or inscription=="0":
                            if "not" in list1[0]:
                                output=list1[0].split(" ")[1]
                            else:
                                output=list1[0]
                            temp.edge(inputs+"->"+outputs,output,label=inscription,arrowhead=arrowstyle)
                        else:
                            temp.edge(inputs+"->"+outputs,list1[0],label=inscription)
                    


                    temp.node(list1[0],list1[0],xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")
                    if "not" in list1[0]:
                        output=list1[0].split(" ")[1]
                    else:
                        output=list1[0]
                    if not output in self.PN_places:
                        self.PN_places.append(output)
            # print(inputs,outputs)
        return temp
        
    def reparse(self,graph):
        text=graph.source
        line=text.split("\n")
        result=[]
        for i in line:
            if  "\"" in i:
                result.append(i.split("\t")[1])
        return result
    
    def to_PNML(self,filename,graph):
        global SingleToken
        blankPNML_path=script_path+"/Support/BlankPNML2.xml"
        
        SingleToken=True


        # Parse the behavior tree and construct the PNML
        blankPNML=ET.parse(blankPNML_path)
        PNMLroot=blankPNML.getroot()[0]

        # Extract the templates from the file
        Templatetree2 = ET.parse(script_path+"/Support/PN_templates.xml")
        Templateroot2 = Templatetree2.getroot()


        for i in graph.source.split("\n"):
            if "circle" in i:
                print({i.split(" ")[0].split("\t")[1]})
                new_place=createPT1(Templateroot2,"place",i.split(" ")[0].split("\t")[1])
                if i.split(" ")[0].split("\t")[1]=="R_T":
                    new_place=modifyField(new_place,"initialMarking/value","1","text")
                else:
                    new_place=modifyField(new_place,"initialMarking/value","0","text")
                
                
                PNMLroot.append(new_place)
            elif "width=0.7" in i:
                
                ends=[x for x in re.split(r'\t| | -> |\[|\]',i) if x]
                name=[x for x in re.split(r'\"|(->)',ends[0]) if x]
                fin_name=""
                for k in name:
                    if k=="->":
                        fin_name+="--"
                    else:
                        fin_name+=k
                ends[0]=fin_name
                new_place=createPT1(Templateroot2,"transition",ends[0])
                
                for k in ends:
                    if "label" in k and not "xlabel" in k:
                        if not k.split("label=")[1]=="\"\"":
                            new_place=modifyField(new_place,"priority/value",k.split("label=")[1],"text")
                # print(re.split(r'\"|\\| -> ',i)[1],re.split(r'\"|\\| -> ',i)[2])
                

                PNMLroot.append(new_place)

            elif "square" in i:
                pass
            else:
                # print([x for x in re.split(r'\t|\"| -> |\[',i) if x])
                elements=[x for x in re.split(r'\t| -> |\[|digraph {|}',i) if x and not x==' ']
                
                if len(elements)>0:
                    input=re.split(r'(->)',elements[0])
                    input_string=""
                    for k in input:
                        if k=="->":
                            input_string+="--"
                        else:
                            input_string+=k

                    output=re.split(r'(->)',elements[1])
                    output_string=""
                    for k in output:
                        if k=="->":
                            output_string+="--"
                        else:
                            output_string+=k
                    attributes=[x for x in re.split(r'=| |]',elements[2]) if x]
                    attr=[]
                    for j in range(len(attributes)-1):
                        attr.append((attributes[j],attributes[j+1]))
                    
                    attr=dict(attr)
                    
                    try:
                        inscription=str(int(attr["label"]))
                    except:
                        inscription=[x for x in re.split(r'"|\+',attr["label"]) if x][1]
                    # print(input_string,output_string,inscription)
                    # print(elements,elements[0],elements[1],attr)
                    if "\"" in input_string:
                        temp=input_string.split("\"")[1]
                        in_string=f"{temp}".replace("&","and")
                    else:
                        temp=input_string
                        in_string=f"{input_string}"
                    if "\"" in output_string:
                        temp=output_string.split("\"")[1]
                        out_string=f"{temp}".replace("&","and")
                    else:
                        out_string=f"{output_string}"
                    new_arc=generateArc(Templateroot2,in_string,out_string,"normal",inscription)
                   
                    PNMLroot.append(new_arc)    
        blankPNML.write(filename+".xml")
        f = open(filename+".xml", "r+")
        content = f.read()
        f.seek(0, 0)
        f.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"+content)
        f.close()

    def to_JANI(self,filename):
        global SingleToken
        
        # Opening JSON file
        f = open(script_path+'/Support/test.jani')
        
        # returns JSON object as a dictionary
        gs.jani_structure= json.load(f)
        # print(self.variables_list)
        for i in self.variables_list:
            if "I" in i:
                continue
            name=i.split("=")[0]
            if name=="R_T":
                assignment=1
            else:
                assignment=0
            
            initial_assignment={}
            initial_assignment["initial-value"]=assignment
            initial_assignment["name"]=name
            initial_assignment["type"]="int"
            if not initial_assignment in gs.jani_structure["variables"]:
                gs.jani_structure["variables"].append(initial_assignment)

        for i in self.edge_list:
            input_vector=i[0]
            output_vector=i[1]
            if "style" in dict(self.edge_dict[i[0]+"->"+i[1]].attributes).keys():
                if dict(self.edge_dict[i[0]+"->"+i[1]].attributes)["style"]=="dashed":
                    # print(i[0]+"->"+i[1])
                    if "I" in i[0]:
                        temporary=i[0].split("I")[0]+i[0].split("I")[1]
                        input_vector=temporary
                    else:
                        continue
            if "color" in dict(self.edge_dict[i[0]+"->"+i[1]].attributes).keys():
                if dict(self.edge_dict[i[0]+"->"+i[1]].attributes)["color"]=="green":
                    continue
            if "label" in dict(self.edge_dict[i[0]+"->"+i[1]].attributes).keys():
                priority=dict(self.edge_dict[i[0]+"->"+i[1]].attributes)["label"]
            else:
                priority=1
            input_vector=input_vector.split("\"")[1]
            output_vector=output_vector.split("\"")[1]
            create_assignment(input_vector,output_vector,int(priority),gs.jani_structure)
            
        # Writing to sample.json
        with open(filename+".jani", "w", encoding='utf8') as outfile:
            json.dump(gs.jani_structure, outfile, ensure_ascii=False, indent=4)

def main():
    global blankPNML, P,Unsumm_nodes, F, G    
    filename = askopenfilename(initialdir=script_path+"/Inputs") # show an "Open" dialog box and return the path to the selected input file
    # Extract the behavior tree from its file
    tree = ET.parse(filename) # extract the bt in cml format
    root = tree.getroot() # take its root
    for i in root: # if it is a more structured file it looks for the Behavior Tree tag
        if i.tag=="BehaviorTree":
            root=i
            break
    parseBT(root, "",optimization_=False) # Parse the Bt
    # Draw the directed graph
    P.render(script_path+"/Outputs/Images/Unoptimized_transition_graph",format='png')
    edgelist=get_edges(P)
    G=nx.DiGraph(edgelist)    
    F=Digraph(format='gv')
    F.engine="dot"
    Q=nx.DiGraph()
    for i in G.nodes():
        if i.split("\"")[1] in Unsumm_nodes:
            floodFill(G,i,Q)
    temp_graph=Graph(F)
    for i in temp_graph.edges:
        start=i.label.split(" -> ")[0].split("\"")[1]
        end=i.label.split(" -> ")[1].split("\"")[1]
        if "I" in start or "I" in end:
            i.attributes.append(("style","dashed"))

    F=temp_graph.construct_graph()
    # for i in Unsumm_nodes:
    #     F.node(i,i,style="filled",color='lightblue')
    F.render(script_path+"/Outputs/Images/Execution_flow_graph_opt",format='png')
    K=temp_graph.construct_PN(contracted=True)
    temp_graph.to_PNML(script_path+"/Outputs/PNML/Optimized_PN",K)
    
    
if __name__ == '__main__':
    main()