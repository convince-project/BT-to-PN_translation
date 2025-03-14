from PN_parser import *
from Optimization_support import *
from tkinter.filedialog import askopenfilename
from typing import Tuple, List, Iterable
from pydot import Dot, graph_from_dot_data, Edge
from graphviz.graphs import BaseGraph
from graphviz import Source
import networkx as nx
from networkx.drawing.nx_pydot import read_dot
import PN_support
import re
from io import StringIO
import pprint

import matplotlib.pyplot as plt

script_path = os.path.abspath(__file__)
script_path=os.path.dirname(os.path.dirname(script_path))

report={
    "BT":{
        "nodes":0,
        "unoptimized_transition_graph":"",
        "optimized_transition_graph":""
    },
    "Unoptimized":{
        "PNML":{
            "nodes":0,
            "transitions":0,
            "arcs":0,
            "creation_time":0
        },
        "JANI":{
            "edges":0,
            "variables":0,
            "creation_time":0
        }
    },
    "Optimized":{
        "PNML":{
            "nodes":0,
            "transitions":0,
            "arcs":0,
            "creation_time":0
        },
        "JANI":{
            "edges":0,
            "variables":0,
            "creation_time":0
        }
    }
}

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
            Unsumm_nodes.append("R_A=1")
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
        elif tree.tag=="ForceFailure":
            CreateForceFailure(tree,name)
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

def read_dot_from_text_networkx(dot_text):
        dot_file = StringIO(dot_text)
        V = nx.DiGraph(nx.nx_pydot.read_dot(dot_file))

        return V

def correct_and_update_sequence(sequence):
    corrected_sequence = []
    standalone_valid_nodes = {}
    invalid_nodes = {}

    # First pass to record valid standalone nodes
    for idx, (cond, val, color, valid) in enumerate(sequence):
        if '&' not in cond.strip():
            if valid:
                standalone_valid_nodes[cond.strip()] = idx
            else:
                invalid_nodes[cond.strip()] = idx

    # Keep track of indexes of valid nodes
    valid_indexes = [idx for idx, node in enumerate(sequence) if node[3]]

    idx = 0
    while idx < len(sequence):
        cond, val, color, valid = sequence[idx]

        if not valid:
            idx += 1
            continue  # Skip invalid standalone nodes

        # Handle composite conditions replacements
        if '&' in cond:
            terms = [term.strip() for term in cond.split('&')]
            new_terms = []
            for term in terms:
                if term in invalid_nodes:
                    invalid_idx = invalid_nodes[term]
                    if invalid_idx < idx:
                        # Replace with previous valid node
                        prev_valid = [
                            node for node, vidx in standalone_valid_nodes.items()
                            if vidx < invalid_idx
                        ]
                        replacement = prev_valid[-1] if prev_valid else term
                    else:
                        # Replace with next valid node
                        next_valid = [
                            node for node, vidx in sorted(standalone_valid_nodes.items(), key=lambda x: x[1])
                            if vidx > invalid_idx
                        ]
                        replacement = next_valid[0] if next_valid else term
                    new_terms.append(replacement)
                else:
                    new_terms.append(term)
            cond = ' & '.join(new_terms)

        # Check for green nodes and max priority between current and next valid node
        current_valid_idx = idx
        next_valid_idx = None
        for vi in valid_indexes:
            if vi > current_valid_idx:
                next_valid_idx = vi
                break

        if next_valid_idx:
            # Analyze nodes between current and next valid
            between_nodes = sequence[current_valid_idx + 1:next_valid_idx]

            # Check if there's a green node
            is_green_present = any(node[2] == 'green' for node in between_nodes)

            # Find highest priority
            priorities = [int(node[1]) for node in between_nodes]
            highest_priority = str(max(priorities)) if priorities else sequence[next_valid_idx][1]

            # Modify next valid node accordingly
            next_cond, next_val, next_color, next_valid = sequence[next_valid_idx]
            next_color = 'green' if is_green_present else next_color
            next_val = highest_priority
            sequence[next_valid_idx] = (next_cond, next_val, next_color, next_valid)

        corrected_sequence.append((cond, val, color, valid))
        idx += 1

    return corrected_sequence


def floodFill(G,node,Q,edge_list,trace=[],contract=False):
    out_arcs=G.out_edges(node)
    for i in out_arcs: # For the arcs going out of the node
        x=edge_list[(i[0].split("\"")[1],i[1].split("\"")[1])]["label"]
        if "color" in edge_list[(i[0].split("\"")[1],i[1].split("\"")[1])]:
            y=edge_list[(i[0].split("\"")[1],i[1].split("\"")[1])]["color"]
        else:
            y=""
        priority=0
        priority = x if not x=="\"\"" else 1
        if i[1].split("\"")[1] in Unsumm_nodes: # if the node is important
            if trace==[]: # If the current trace is empty
                if not Q.has_edge(i[0],i[1]): #If the current arc is not in the temporary graph
                    F.edge(i[0].split("\"")[1],i[1].split("\"")[1],label=x) # Put the current edge in the final graph
                    Q.add_edge(i[0],i[1]) # Add the edge to the temporary graph
            else:
                temp=copy.deepcopy(trace)
                keeper=True if i[1].split("\"")[1] in Unsumm_nodes or i[1].split("\"")[1] in Aux_nodes else False
                temp.append((i[1].split("\"")[1],priority,y,keeper))
                corrected_sequence=correct_and_update_sequence(temp)
                for k in range(len(corrected_sequence)-1): # reading through the temp trace
                    idx1=k
                    idx2=k+1
                    if not Q.has_edge(corrected_sequence[idx1][0],corrected_sequence[idx2][0]): #If the current arc is not in the temporary graph
                        if not corrected_sequence[idx2][2]=="":
                            F.edge(corrected_sequence[idx1][0],corrected_sequence[idx2][0],color="green",label=corrected_sequence[idx2][1]) # Put the current edge in the final graph
                            Q.add_edge(corrected_sequence[idx1][0],corrected_sequence[idx2][0]) # Add the edge to the temporary graph
                        else:
                            F.edge(corrected_sequence[idx1][0],corrected_sequence[idx2][0],label=corrected_sequence[idx2][1]) # Put the current edge in the final graph
                            Q.add_edge(corrected_sequence[idx1][0],corrected_sequence[idx2][0]) # Add the edge to the temporary graph                           
        else:
            temp_trace=copy.copy(trace)
            if temp_trace==[]:
                keeper=True if i[0].split("\"")[1] in Unsumm_nodes or i[0].split("\"")[1] in Aux_nodes else False
                temp_trace.append((i[0].split("\"")[1],priority,"",keeper))
            keeper=True if i[1].split("\"")[1] in Unsumm_nodes or i[1].split("\"")[1] in Aux_nodes else False
            temp_trace.append((i[1].split("\"")[1],priority,y,keeper))
            floodFill(G,i[1],Q,edge_list,trace=temp_trace)

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
        start=time.time()
        self.text=graph.pipe(engine="osage",format='dot').decode('latin-1')
        end=time.time()
        self.xmax=1000
        self.xmin=0
        self.ymax=2000
        self.ymin=0
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
                self.edge_list.append((x,y,temp_edge.attributes))
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
            edge_label=i

            if not "color" in dict(i[2]):
                pass                
            else:
                continue
            
            inputs=i[0].split("\"")[1]
            outputs=i[1].split("\"")[1]

            edge_label="->".join([inputs,outputs])
            label=dict(i[2])

            edge={
                  "inputs":inputs,
                  "outputs":outputs,
                  "attributes":label,
                  "edge_label":edge_label,
                  "inputs_nodes":inputs.split(" & "),
                  "outputs_nodes":outputs.split(" & ")
                  }
            temp.node(edge_label,edge["attributes"]["label"],xlabel="", style = 'filled', color = 'black', shape = "box", width="0.7", height="0.14",fontcolor='white',fontname="arial bold")
            
            for i in edge["inputs_nodes"]:
                match = re.search(r'not\((.*?)\)', i)
                result=match.group(1) if match else None
                if result:
                    assignment=result.split("=")
                    if len(assignment)>1:
                        node=assignment[0]
                        label=assignment[1]
                    else:
                        node=assignment[0]
                        label="0"
                    temp.edge(node,edge["edge_label"],label=label,arrowhead="odot")
                    temp.node(node,node,xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")
                else:
                    assignment=i.split("=")
                    if len(assignment)>1:
                        node=assignment[0]
                        label=assignment[1]
                    else:
                        node=assignment[0]
                        label="0"
                    temp.edge(node,edge["edge_label"],label=label)
                    temp.node(node,node,xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")

            
            for i in edge["outputs_nodes"]:
                match = re.search(r'R\((.*?)\)', i)
                result=match.group(1) if match else None
                if result:
                    assignment=result.split("=")
                    if len(assignment)>1:
                        node=assignment[0]
                        label=assignment[1]
                    else:
                        node=assignment[0]
                        label="0"
                    temp.edge(edge["edge_label"],node,label=label,arrowhead="odiamond")
                    temp.node(node,node,xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")
                else:
                    assignment=i.split("=")
                    if len(assignment)>1:
                        node=assignment[0]
                        label=assignment[1]
                    else:
                        node=assignment[0]
                        label="0"
                    temp.edge(edge["edge_label"],node,label=label)
                    temp.node(node,node,xlabel="", style = 'filled', color = "black", fillcolor="white", shape = "circle")

        return temp

    def reparse(self,graph):
        text=graph.source
        line=text.split("\n")
        result=[]
        for i in line:
            if "node" in i:
                pass
            elif "digraph" in i:
                pass
            elif "graph" in i:
                pass
            elif  "\"" in i:
                result.append(i.split("\t")[1])
            
        return result
    
    def compileFinal(tree,text,type):
        global xmin,ymin,xmax,ymax
        for rank in tree.iter(type):
            first_index=text.find(rank.attrib['id'])
            second_index=text.find(";",first_index)
            third_index=text.find("pos",first_index,second_index)
            fourth_index=text.find("\",",third_index,second_index)
            delim=text.find(",",third_index+4,fourth_index+1)-third_index-5
            x=float(text[third_index+5:third_index+5+delim])
            y=float(text[third_index+6+delim:fourth_index])
            if x>xmax:
                xmax=x
            elif x<xmin:
                xmin=x
            else:
                pass
            if y>ymax:
                ymax=y
            elif y<ymin:
                ymin=y
            else:
                pass

    def reorganizeFinal(root,text,PNMLroot,type):
        for rank in root.iter(type):
                first_index=text.find(rank.attrib['id'])
                second_index=text.find(";",first_index)
                third_index=text.find("pos",first_index,second_index)
                fourth_index=text.find("\",",third_index,second_index)
                delim=text.find(",",third_index+4,fourth_index+1)-third_index-5
                x=float(text[third_index+5:third_index+5+delim])
                y=float(text[third_index+6+delim:fourth_index])
                xpar=(x-xmin)/(xmax-xmin)
                ypar=(y-ymin)/(ymax-ymin)
                if yinvert:
                    ypar=1-ypar
                if xinvert:
                    xpar=1-xpar
                try:
                    rank=modifyField(rank,"position",{"x":str(xcmin+((xcmax-xcmin)*xpar)),
                                                    "y":str(ycmin+((ycmax-ycmin)*ypar))},"attrib")
                except:
                    temp=ET.Element("graphics")
                    temp=makeField(temp,"position",{'attrib':{"x":str(xcmin+((xcmax-xcmin)*xpar)),
                                                            "y":str(ycmin+((ycmax-ycmin)*ypar))},'text':{}})
                    rank.append(temp)
                PNMLroot.append(rank)


    def to_PNML(self,filename,graph):
        global SingleToken, report
        blankPNML_path=script_path+"/Support/BlankPNML2.xml"
        SingleToken=True
        # Parse the behavior tree and construct the PNML
        blankPNML=ET.parse(blankPNML_path)
        PNMLroot=blankPNML.getroot()[0]
        places=[]
        transitions=[]
        arcs=[]

        # Extract the templates from the file
        Templatetree2 = ET.parse(script_path+"/Support/PN_templates.xml")
        Templateroot2 = Templatetree2.getroot()
        start=time.time()
        a1=graph.pipe(engine="osage",format='dot').decode('latin-1')
        end=time.time()
        # Read the DOT file
        G = read_dot_from_text_networkx(a1)
        # Remove the graph line from the text
        dot_text = re.findall(r'graph \[.*?\];', a1,flags=re.DOTALL)
        x_min, y_min, x_max, y_max = map(float, dot_text[0].split("\"")[1].split(","))
        nodes=dict(G.nodes(data=True))
        start=time.time()
        for i in graph.source.split("\n"):
            if "circle" in i:
                name=i.split(" ")[0].split("\t")[1]
                new_place=createPT1(Templateroot2,"place",i.split(" ")[0].split("\t")[1])
                if i.split(" ")[0].split("\t")[1]=="R_T":
                    new_place=modifyField(new_place,"initialMarking/value","1","text")
                else:
                    new_place=modifyField(new_place,"initialMarking/value","0","text")
                
                pos=nodes[name]["pos"].split("\"")[1]
                x=float(pos.split(",")[0])
                y=float(pos.split(",")[1])

                xpar=(x-x_min)/(x_max-x_min)
                ypar=(y-y_min)/(y_max-y_min)
                if yinvert:
                    ypar=1-ypar
                if xinvert:
                    xpar=1-xpar
                
                new_place=modifyField(new_place,
                                    "graphics/position",
                                    {"x":f"{self.xmin+((self.xmax-self.xmin)*xpar):.2f}",
                                     "y":f"{self.ymin+((self.ymax-self.ymin)*ypar):.2f}"},
                                    "attrib")
                if not name in places:
                    PNMLroot.append(new_place)
                    places.append(name)
            elif "width=0.7" in i:
                
                ends=[x for x in re.split(r'\t|\[',i) if x]                
                fin_name=ends[0].replace("->","--").replace("&","and").split("\"")[1]
                new_place=createPT1(Templateroot2,"transition",fin_name)
                label=nodes[ends[0].split("\"")[1]]["label"]
                new_place=modifyField(new_place,"priority/value",label,"text")                

                name=" ".join(ends[0:3]).split("\"")[1]
                pos=nodes[name]["pos"].split("\"")[1]
                x=float(pos.split(",")[0])
                y=float(pos.split(",")[1])

                xpar=(x-x_min)/(x_max-x_min)
                ypar=(y-y_min)/(y_max-y_min)
                if yinvert:
                    ypar=1-ypar
                if xinvert:
                    xpar=1-xpar
                
                new_place=modifyField(new_place,
                                    "graphics/position",
                                    {"x":f"{self.xmin+((self.xmax-self.xmin)*xpar):.2f}",
                                     "y":f"{self.ymin+((self.ymax-self.ymin)*ypar):.2f}"},
                                    "attrib")


                if not fin_name in transitions:
                    PNMLroot.append(new_place)
                    transitions.append(fin_name)

            elif "square" in i:
                pass
            else:
                elements=[x for x in re.split(r'\t| -> |\[|digraph {|}',i) if x and not x==' ']
                if len(elements)>0:
                    el0="".join(elements[0].split("\"")[1]) if "\"" in elements[0] else elements[0]
                    el1="".join(elements[1].split("\"")[1]) if "\"" in elements[1] else elements[1]
                    input_string=el0.replace("->","--").replace("&","and")
                    output_string=el1.replace("->","--").replace("&","and")
                    attributes=[x for x in re.split(r'=| |]',elements[2]) if x]
                    attr=[]
                    for j in range(len(attributes)-1):
                        attr.append((attributes[j],attributes[j+1]))
                    
                    attr=dict(attr)
                    try:
                        inscription=str(int(attr["label"]))
                    except:
                        inscription=[x for x in re.split(r'"|\+',attr["label"]) if x][1]
                    if "\"" in input_string:
                        temp=input_string.split("\"")[1]
                        in_string=f"{temp}".replace("&","and")
                        if in_string[-1]==" ":
                            in_string=in_string[:-1]
                    else:
                        temp=input_string
                        in_string=f"{input_string}"
                        if in_string[-1]==" ":
                            in_string=in_string[:-1]
                    if "\"" in output_string:
                        temp=output_string.split("\"")[1]
                        out_string=f"{temp}".replace("&","and")
                        if out_string[-1]==" ":
                            out_string=out_string[:-1]
                    else:
                        out_string=f"{output_string}"
                        if out_string[-1]==" ":
                            out_string=out_string[:-1]
                    
                    new_arc=generateArc(Templateroot2,in_string,out_string,"normal",inscription)
                    fin_name=" to ".join([in_string,out_string])
                    if not fin_name in arcs:
                        PNMLroot.append(new_arc)    
                        arcs.append(fin_name)
        end=time.time()
        if "Unoptimized" in filename:
            report["Unoptimized"]["PNML"]["nodes"]=len(nodes)
            report["Unoptimized"]["PNML"]["transitions"]=len(transitions)
            report["Unoptimized"]["PNML"]["arcs"]=len(arcs)
            report["Unoptimized"]["PNML"]["creation_time"]=end-start
        elif "Optimized" in filename:
            report["Optimized"]["PNML"]["nodes"]=len(nodes)
            report["Optimized"]["PNML"]["transitions"]=len(transitions)
            report["Optimized"]["PNML"]["arcs"]=len(arcs)
            report["Optimized"]["PNML"]["creation_time"]=end-start
        else:
            pass
        # Ensure the directory exists before opening the file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        blankPNML.write(filename+".xml")
        f = open(filename+".xml", "r+")
        content = f.read()
        f.seek(0, 0)
        f.write("<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"+content)
        f.close()

    def to_JANI(self,filename,graph):
        global report
        # Opening JSON file
        f = open(script_path+'/Support/test.jani')
        
        start=time.time()
        a1=graph.pipe(engine="osage",format='dot').decode('latin-1')
        end=time.time()
        # Read the DOT file
        G = read_dot_from_text_networkx(a1)
        # Remove the graph line from the text
        dot_text = re.findall(r'graph \[.*?\];', a1,flags=re.DOTALL)
        x_min, y_min, x_max, y_max = map(float, dot_text[0].split("\"")[1].split(","))

        # returns JSON object as a dictionary
        gs.jani_structure= json.load(f)
        nodes=dict(G.nodes(data=True))
        transition_counter=0
        start=time.time()
        for i in graph.source.split("\n"):
            if "circle" in i:
                name=i.split(" ")[0].split("\t")[1]
                
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
            elif "width=0.7" in i:
                ends=[x for x in re.split(r'\t|\[',i) if x]                
                fin_name=ends[0].replace("->","--").replace("&","and").split("\"")[1]
                input_vector=" & ".join(fin_name.split("--")[0].split(" and "))
                output_vector=" & ".join(fin_name.split("--")[1].split(" and "))
                priority=nodes[ends[0].split("\"")[1]]["label"]
                transition_counter+=1
                create_assignment(input_vector,output_vector,int(priority),gs.jani_structure)
        end=time.time()

        if "Unoptimized" in filename:
            report["Unoptimized"]["JANI"]["variables"]=len(gs.jani_structure["variables"])
            report["Unoptimized"]["JANI"]["edges"]=transition_counter
            report["Unoptimized"]["JANI"]["creation_time"]=end-start
        elif "Optimized" in filename:
            report["Optimized"]["JANI"]["variables"]=len(gs.jani_structure["variables"])
            report["Optimized"]["JANI"]["edges"]=transition_counter
            report["Optimized"]["JANI"]["creation_time"]=end-start
        else:
            pass
        # Ensure the directory exists before opening the file
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Writing to sample.json
        with open(filename+".jani", "w", encoding='utf8') as outfile:
            json.dump(gs.jani_structure, outfile, ensure_ascii=False, indent=4)
  
def count_nodes(node):
    """Count all nodes under an ET node, including itself."""
    return 1 + sum(count_nodes(child) for child in node)

def main():
    global blankPNML, P,Unsumm_nodes, F, G, report
    filename = askopenfilename(initialdir=script_path+"/Inputs") # show an "Open" dialog box and return the path to the selected input file
    folder=os.path.basename(filename).split(".")[0]
    # Extract the behavior tree from its file
    tree = ET.parse(filename) # extract the bt in cml format
    root = tree.getroot() # take its root
    for i in root: # if it is a more structured file it looks for the Behavior Tree tag
        if i.tag=="BehaviorTree":
            root=i
            break
    report["BT"]["nodes"]=count_nodes(i)
    parseBT(root, "") # Parse the Bt
    print("Parsed BT")
    # Depict unoptimized graph

    temp_graph=Graph(P)
    for i in temp_graph.edges:
        start=i.label.split(" -> ")[0].split("\"")[1]
        end=i.label.split(" -> ")[1].split("\"")[1]
        if "I" in start or "I" in end:
            i.attributes.append(("style","dashed"))
    print("Constructed BT graph")
    F=temp_graph.construct_graph()
    print("Constructed Unoptimized transition graph")

    F.render(script_path+"/Outputs/Images/"+folder+"/Unoptimized_transition_graph",format='png',engine="osage")
    report["BT"]["unoptimized_transition_graph"]=script_path+"/Outputs/Images/"+folder+"/Unoptimized_transition_graph.png"
    
    K=temp_graph.construct_PN(contracted=True)
    print("Constructed Unoptimized PN")

    K.render(script_path+"/Outputs/Images/"+folder+"/Unoptimized_PN_image",format='png',engine="osage")
    temp_graph.to_PNML(script_path+"/Outputs/PNML/"+folder+"/Unoptimized_PN",K)
    print("Constructed Unoptimized PNML")

    temp_graph.to_JANI(script_path+"/Outputs/JANI/"+folder+"/Unoptimized_jani",K)
    print("Constructed Unoptimized JANI")

    # Depict optimized version

    edgelist=get_edges(P)
    G=nx.DiGraph(edgelist)    
    F=Digraph(format='gv')
    F.engine="dot"
    Q=nx.DiGraph()
    R=read_dot_from_text_networkx(P.source)
    edges=dict(R.edges(data=False))
    for i in G.nodes():
        if i.split("\"")[1] in Unsumm_nodes:
            floodFill(G,i,Q,edges)
    temp_graph=Graph(F)
    print("Finished optimization")

    for i in temp_graph.edges:
        start=i.label.split(" -> ")[0].split("\"")[1]
        end=i.label.split(" -> ")[1].split("\"")[1]
        if "I" in start or "I" in end:
            i.attributes.append(("style","dashed"))
    F=temp_graph.construct_graph()
    print("Constructed graph")
    F.render(script_path+"/Outputs/Images/"+folder+"/Optimized_transition_graph",format='png',engine="osage")
    report["BT"]["optimized_transition_graph"]=script_path+"/Outputs/Images/"+folder+"/Optimized_transition_graph.png"
    K=temp_graph.construct_PN(contracted=True)
    print("Constructed Optimized PN")
    K.render(script_path+"/Outputs/Images/"+folder+"/Optimized_PN_image",format='png',engine="osage")
    temp_graph.to_PNML(script_path+"/Outputs/PNML/"+folder+"/Optimized_PN",K)
    print("Constructed Optimized PNML")
    temp_graph.to_JANI(script_path+"/Outputs/JANI/"+folder+"/Optimized_jani",K)
    print("Constructed Optimized JANI")

    filename=script_path+"/Outputs/reports/"+folder+".json"
    # Ensure the directory exists before opening the file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(report, file, indent=4, sort_keys=True)

    
    
    
if __name__ == '__main__':
    main()