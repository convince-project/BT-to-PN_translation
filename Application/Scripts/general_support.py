from typing import Tuple, List, Iterable
from pydot import Dot, graph_from_dot_data, Edge
from graphviz.graphs import BaseGraph
from graphviz import Source, Digraph
import math
import os
import time
import sys
import xml.etree.ElementTree as ET
import copy,graphviz
import json

ControlFlow=["ReactiveSequence",
           "Sequence", # Sequence with memory
           "ReactiveFallback",
           "Fallback", # Fallback with memory
           "Parallel",
           "Inverter",
           "ForceSuccess",
           "ForceFailure",
           "RetryUntilSuccessful",
           "Switch2"]

Execution=["BtCondition",
           "BtAction"]

BT_index=str(format(1,'01x'))

LeafMap=[]
explored_leafs=0
for_save=True
xcmax=700
xcmin=0
ycmax=300
ycmin=0
yinvert=True
xinvert=False
xmax=-math.inf
xmin=math.inf
ymax=-math.inf
ymin=math.inf

jani_structure={}

engine_list=["dot", "fdp", "neato", "circo", "twopi", "osage"]

# JSON encoder class to save the file
class MyEncoder(json.JSONEncoder):
    def default(self, o):
        if type(o) is bytes:
            return o.decode("utf-8")
        return super(MyEncoder, self).default(o)


def findCondition(Templates,i):
    listing=Templates.findall('.//*[@id="'+i.tag+'"]')[0]
    for j in listing:
        if j.tag=="ReturnCond":
            newcond=j.text # Returning condition of the node
            return newcond

def findElementbyID(Tree,element):
    return Tree.findall('.//*[@id="'+element+'"]')[0]

def findElementbyTag(Tree,element):
    return Tree.findall(element)[0]

def TreeSubElement(Tree,array):
    if Tree.tag=="Composite":
        Tree=array[int(Tree.attrib["name"])]
        return Tree
    else:
        for i in Tree:
            Tree[list(Tree).index(i)]=TreeSubElement(i,array)
        return Tree

def printTree(Tree,depth):
    print("\t"*depth,Tree.tag,Tree.attrib,Tree.text)
    depth=depth+1
    for i in Tree:
        printTree(i,depth)

def modifyTemplate(Templates,xml,field,value,attribute):
    xml=findElementbyID(Templates,xml)[0]
    new=copy.deepcopy(xml)
    if attribute=="text":
        new.find('.//'+field).text=value
    elif attribute=="tag":
        new.find('.//'+field).tag=value
    elif attribute=="attrib":
        new.find('.//'+field).attrib=value
    return new

def modifyField(xml,field,value,attribute):
    new=copy.deepcopy(xml)
    if attribute=="text":
        new.find('.//'+field).text=value
    elif attribute=="tag":
        new.find('.//'+field).tag=value
    elif attribute=="attrib":
        new.find('.//'+field).attrib=value
    return new

def makeField(xml,field,value):
    new=copy.deepcopy(xml)
    newSub = ET.SubElement(new, field)
    newSub.attrib=value['attrib']
    newSub.text=value['text']
    return new

def generate_name(reference,short,index,full=True):
    if full:
        return "BT"+BT_index+short+str(format(index,'01x')+reference)
    else:
        return str(reference)

def edge_to_node_ids(edge: Edge) -> Tuple[str, str]:
    """Returns the node id pair for the edge object"""
    return (edge.get_source(), edge.get_destination())

def get_graph_dot_obj(graph_spec) -> List[Dot]:
    """Get a dot (graphs) object list from a variety of possible sources (postelizing inputs here)"""
    _original_graph_spec = graph_spec
    if isinstance(graph_spec, (BaseGraph, Source)):
        # get the source (str) from a graph object
        graph_spec = graph_spec.source
    if isinstance(graph_spec, str):
        # get a dot-graph from dot string data
        graph_spec = graph_from_dot_data(graph_spec)
    # make sure we have a list of Dot objects now
    assert isinstance(graph_spec, list) and all(
        isinstance(x, Dot) for x in graph_spec
    ), (
        f"Couldn't get a proper dot object list from: {_original_graph_spec}. "
        f"At this point, we should have a list of Dot objects, but was: {graph_spec}"
    )
    return graph_spec

def get_edges(graph_spec, postprocess_edges=edge_to_node_ids):
    """Get a list of edges for a given graph (or list of lists thereof).
    If ``postprocess_edges`` is ``None`` the function will return ``pydot.Edge`` objects from
    which you can extract any information you want.
    By default though, it is set to extract the node pairs for the edges, and you can
    replace with any function that takes ``pydot.Edge`` as an input.
    """
    graphs = get_graph_dot_obj(graph_spec)
    n_graphs = len(graphs)

    if n_graphs > 1:
        return [get_edges(graph, postprocess_edges) for graph in graphs]
    elif n_graphs == 0:
        raise ValueError(f"Your input had no graphs")
    else:
        graph = graphs[0]
        edges = graph.get_edges()
        if callable(postprocess_edges):
            edges = list(map(postprocess_edges, edges))
        return edges

def get_nodes(graph_spec):
    """Get a list of edges for a given graph (or list of lists thereof).
    If ``postprocess_edges`` is ``None`` the function will return ``pydot.Edge`` objects from
    which you can extract any information you want.
    By default though, it is set to extract the node pairs for the edges, and you can
    replace with any function that takes ``pydot.Edge`` as an input.
    """
    graphs = get_graph_dot_obj(graph_spec)
    n_graphs = len(graphs)

    if n_graphs > 1:
        return [get_nodes(graph) for graph in graphs]
    elif n_graphs == 0:
        raise ValueError(f"Your input had no graphs")
    else:
        graph = graphs[0]
        edges = graph.get_nodes()
        return edges

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
            print(x,y,xmin,ymin)
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

def find_first_element_with_string(list_of_dicts, key, target_string):
        for d in list_of_dicts:
            if key in d and target_string in d[key]:
                return d
        return None
