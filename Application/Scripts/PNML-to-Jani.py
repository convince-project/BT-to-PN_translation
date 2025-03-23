from PN_parser import *
from Optimization_support import *
from tkinter.filedialog import askopenfilename
from typing import Tuple, List, Iterable
import PN_support
import re
from io import StringIO
import pprint
import copy

script_path = os.path.abspath(__file__)
script_path=os.path.dirname(os.path.dirname(script_path))

def to_JANI(filename,graph):
    global report
    # Opening JSON file
    f = open(script_path+'/Support/template.jani')
    
    
    for i in graph.source.split("\n"):
        if "circle" in i:
            name=i.split(" ")[0].split("\t")[1]
            if len(name.split("\"")) >1:
                name=name.split("\"")[1]
            if name==f"{root_name}_T":
                assignment=1
            else:
                assignment=0
            initial_assignment={}

            if name in custom_places.keys():
                if "initial_value" in custom_places[name].keys():
                    assignment=custom_places[name]["initial_value"]
            initial_assignment["initial-value"]=int(assignment)
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


tree = ET.parse("/home/matt/Desktop/NAS/Projects/PhD/MODELS/BT-to-PN_translation/Evaluations/results/dineros_nets/ac9d7b3d-efaf-44af-a5b2-52a9ab4b2662-flatted-41f89c32-6713-4680-8d51-1d9395cfded7.pnml")
root = tree.getroot()

# Namespace handling
ns = {'pnml': 'http://www.pnml.org/version-2009/grammar/pnml'}
f = open(script_path+'/Support/template.jani')
# returns JSON object as a dictionary
gs.jani_structure= json.load(f)

places = []
transitions = {}
arcs = []

for place in root.findall(".//pnml:place", ns):
    places.append(place)

transition_template={
    "name":"",
    "inputs":[],
    "outputs":[],
}

for transition in root.findall(".//pnml:transition", ns):
    temp_transition=copy.deepcopy(transition_template)
    temp_transition["name"]=transition.attrib["id"]
    transitions[transition.attrib["id"]]=temp_transition

print(transitions)

arc_template={
    "source":"",
    "target":"",
    "type":"normal",
    "inscription":1
}

for arc in root.findall(".//pnml:arc", ns):
    temp_arc=copy.deepcopy(arc_template)
    temp_arc["source"] = arc.attrib['source']
    temp_arc["target"] = arc.attrib['target']
    
    if not arc.find("pnml:toolspecific/pnml:type",ns) is None:
        temp_arc["type"]="inhibitor"

    if temp_arc["source"] in transitions:
        transitions[temp_arc["source"]]["outputs"].append(temp_arc)
    
    if temp_arc["target"] in transitions:
        transitions[temp_arc["target"]]["inputs"].append(temp_arc)

    arcs.append(temp_arc)

for i in places:
    print(i.attrib["id"],i[-1][0].text)

for i in transitions:
    input_string=""
    output_string=""
    for input in transitions[i]["inputs"]:
        if input_string=="":
            if input["type"]=="normal":
                input_string=f"{input["source"]}={input["inscription"]}"
            elif input["type"]=="inhibitor":
                input_string=f"not({input["source"]}={input["inscription"]})"
        else:
            if input["type"]=="normal":
                input_string+=f" & {input["source"]}={input["inscription"]}"
            elif input["type"]=="inhibitor":
                input_string+=f" & not({input["source"]}={input["inscription"]})"
    for output in transitions[i]["outputs"]:
        if output_string=="":
            if output["type"]=="normal":
                output_string=f"{output["target"]}={output["inscription"]}"
            elif output["type"]=="inhibitor":
                output_string=f"not({output["target"]}={output["inscription"]})"
        else:
            if output["type"]=="normal":
                output_string+=f" & {output["target"]}={output["inscription"]}"
            elif output["type"]=="inhibitor":
                output_string+=f" & not({output["target"]}={output["inscription"]})"
    
    transitions[i]["guard"]=input_string
    transitions[i]["assignment"]=output_string
    transitions[i]["description"]=f"{input_string} -> {output_string}"



for i in transitions:
    print(transitions[i]["description"])
    create_assignment(transitions[i]["guard"],transitions[i]["assignment"],1,gs.jani_structure)

for i in places:
    initial_assignment={}
    initial_assignment["initial-value"]=int(i[-1][0].text)
    initial_assignment["name"]=i.attrib["id"]
    initial_assignment["type"]="int"
    if not initial_assignment in gs.jani_structure["variables"]:
        gs.jani_structure["variables"].append(initial_assignment)

print(gs.jani_structure)


evaluation_folder=os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "Evaluations"
    )

filename=f"{evaluation_folder}/results/dineros_nets/dineros_jani"
# Ensure the directory exists before opening the file
os.makedirs(os.path.dirname(filename), exist_ok=True)
# Writing to sample.json
with open(filename+".jani", "w", encoding='utf8') as outfile:
    json.dump(gs.jani_structure, outfile, ensure_ascii=False, indent=4)