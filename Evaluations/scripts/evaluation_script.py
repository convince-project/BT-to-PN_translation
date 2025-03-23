import instrumentation_behaverify as beha
import instrumentation_BT_to_PN as btpn
from itertools import product
import random
import os
import xml.etree.ElementTree as ET
import json
import copy

DOCKER_TAG_behaverify = "behaverify"
DOCKER_TAG_tina = "pnml_docker"
VENUE = beha.VENUE
USER_behaverify = beha.USER
USER_tina = btpn.USER_tina

guard= {
    "exp": {
        "left": {
        },
        "op": "∧",
        "right": {
        }
    }
}

destination={
    "assignments": [],
    "probability": { 
        "exp": "Expression", 
    },
    "location": "loc"
}

edge={
    "destinations":[],
    "guard":{},
    "location":"loc",
    "priority":{
        "exp":1
    },
    
}

def replace_values_recursive(data, replacements):
    """ Recursively traverses the dictionary and replaces values based on the mapping. """
    if isinstance(data, dict):
        print(data.keys(),data.values())
        return {k: replace_values_recursive(v, replacements) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_values_recursive(item, replacements) for item in data]
    elif isinstance(data, int) and data in replacements:
        return replacements[data]  # Replace only if it's an exact match
    return data  # Return unchanged if no replacement needed

def prepare_jani(jani_folder,jani_file,size,model):
    with open(f"{jani_folder}/{jani_file}_jani.jani") as f:
        data=json.load(f)
        edges={}
        edges=copy.deepcopy(data["automata"][0]["edges"])
        jani_variables={}
        jani_variables=copy.deepcopy(data["variables"])
        edge1=copy.deepcopy(edge)
        edge1["guard"]={
                        "exp":{
                                "left": {
                                    "left":"set_xpos",
                                    "op":"=",
                                    "right":0
                                },
                                "op": "∧",
                                "right": {
                                    "left":"set_xgoal",
                                    "op":"=",
                                    "right":1
                                }
                            }
                        }
        edge2=copy.deepcopy(edge)
        edge2["guard"]={
                        "exp":{

                                    "left": {
                                        "left":"set_ypos",
                                        "op":"=",
                                        "right":0
                                    },
                                    "op": "∧",
                                    "right": {
                                        "left":"set_xpos",
                                        "op":"=",
                                        "right":1
                                    }
                                }
                        }
        
        edge3=copy.deepcopy(edge)
        edge3["guard"]={
                        "exp":{
                                    "left": {
                                        "left":"set_xgoal",
                                        "op":"=",
                                        "right":0
                                    },
                                    "op": "∧",
                                    "right": {
                                        "left":"set_ygoal",
                                        "op":"=",
                                        "right":1
                                    }
                                }
                                    
                        }

        edge4=copy.deepcopy(edge)
        edge4["guard"]={
                        "exp":{
                                        "left":"set_ygoal",
                                        "op":"=",
                                        "right":0
                        }
        }

        edge5=copy.deepcopy(edge)
        edge5["guard"]={
                        "exp":{ 
                                "left":{
                                            "left":{
                                                "left": {
                                                    "left":"set_xpos",
                                                    "op":"=",
                                                    "right":1
                                                },
                                                "op": "∧",
                                                "right": {
                                                    "left":"set_xgoal",
                                                    "op":"=",
                                                    "right":1
                                                }
                                            },
                                            "op": "∧",
                                            "right":{
                                                "left": {
                                                    "left":"set_ypos",
                                                    "op":"=",
                                                    "right":1
                                                },
                                                "op": "∧",
                                                "right": {
                                                    "left":"set_ygoal",
                                                    "op":"=",
                                                    "right":1
                                                }
                                            }
                                        },
                                        "op": "∧",
                                        "right":{
                                                "left": {
                                                    "left":"R_T",
                                                    "op":"=",
                                                    "right":0
                                                },
                                                "op": "∧",
                                                "right": {
                                                    "left":"initialized",
                                                    "op":"=",
                                                    "right":0
                                                }
                                        }
                                
                            }
                        }


        assignment1={
                "comment": f"R_T <- {1}",
                "ref": "R_T",
                "value": 1
            }
        assignment2={
                "comment": f"initialized <- {1}",
                "ref": "initialized",
                "value": 1
            }
        temp_destination=copy.deepcopy(destination)
        temp_destination["probability"]["exp"]=1
        temp_destination["assignments"].append(assignment1)
        temp_destination["assignments"].append(assignment2)
        edge5["destinations"].append(temp_destination)
        

        for integer in range(1,size+2):
            # Assignment for the x_pos variable
            assignment1={
                "comment": f"set_xpos <- {1}",
                "ref": "set_xpos",
                "value": 1
            }
            assignment2={
                "comment": f"x_pos <- {integer}",
                "ref": "x_pos",
                "value": integer
            }
            temp_destination=copy.deepcopy(destination)
            temp_destination["probability"]["exp"]=1/size
            temp_destination["assignments"].append(assignment1)
            temp_destination["assignments"].append(assignment2)
            edge1["destinations"].append(temp_destination)

            # Assignment for the y_pos variable
            assignment1={
                "comment": f"set_ypos <- {1}",
                "ref": "set_ypos",
                "value": 1
            }
            assignment2={
                "comment": f"y_pos <- {integer}",
                "ref": "y_pos",
                "value": integer
            }
            temp_destination=copy.deepcopy(destination)
            temp_destination["probability"]["exp"]=1/size
            temp_destination["assignments"].append(assignment1)
            temp_destination["assignments"].append(assignment2)
            edge2["destinations"].append(temp_destination)

            # Assignment for the x_goal variable
            assignment1={
                "comment": f"set_xgoal <- {1}",
                "ref": "set_xgoal",
                "value": 1
            }
            assignment2={
                "comment": f"x_goal <- {integer}",
                "ref": "x_goal",
                "value": integer
            }
            assignment3={
                "comment": f"x_small <- {integer-1}",
                "ref": "x_small",
                "value": integer
            }
            assignment4={
                "comment": f"x_big <- {integer+1}",
                "ref": "x_big",
                "value": integer+1
            }
            temp_destination=copy.deepcopy(destination)
            temp_destination["probability"]["exp"]=1/size
            temp_destination["assignments"].append(assignment1)
            temp_destination["assignments"].append(assignment2)
            temp_destination["assignments"].append(assignment3)
            temp_destination["assignments"].append(assignment4)
            edge3["destinations"].append(temp_destination)

            # Assignment for the y_goal variable
            assignment1={
                "comment": f"set_ygoal <- {1}",
                "ref": "set_ygoal",
                "value": 1
            }
            assignment2={
                "comment": f"y_goal <- {integer}",
                "ref": "y_goal",
                "value": integer
            }
            assignment3={
                "comment": f"y_small <- {integer-1}",
                "ref": "y_small",
                "value": integer
            }
            assignment4={
                "comment": f"y_big <- {integer+1}",
                "ref": "y_big",
                "value": integer+1
            }
            temp_destination=copy.deepcopy(destination)
            temp_destination["probability"]["exp"]=1/size
            temp_destination["assignments"].append(assignment1)
            temp_destination["assignments"].append(assignment2)
            temp_destination["assignments"].append(assignment3)
            temp_destination["assignments"].append(assignment4)
            edge4["destinations"].append(temp_destination)

        edges.append(edge1)
        edges.append(edge2)
        edges.append(edge3)
        edges.append(edge4)
        edges.append(edge5)


        params_file=f"{application_folder}/Inputs/{model}_nodes.xml"
        # Load XML from a file
        tree = ET.parse(params_file)
        root = tree.getroot()  # Get the root element
        xml_variables=root.find(".//constants")
        replacements={}
        for k in xml_variables:
            replacements[k.attrib["value"]]=k.tag


        xml_variables=root.find(".//variables")
        new_variables=[]
        exclusion_list=[i.tag for i in xml_variables]
        for element in jani_variables:
           
            if not element["name"] in exclusion_list:
                variable={
                    "initial-value": 0,
                    "name": element["name"],
                    "type": "int"
                }
                new_variables.append(variable)
        new_variables.append({
                "initial-value": 0,
                "name": "x_pos",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "y_pos",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "set_xpos",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "set_ypos",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "x_goal",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "y_goal",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "set_xgoal",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "set_ygoal",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "reached_goal",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "x_small",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "x_big",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "y_small",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "y_big",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 1,
                "name": "x_min",
                "type": "int"
            })
        new_variables.append({
                "initial-value": size+1,
                "name": "x_max",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 1,
                "name": "y_min",
                "type": "int"
            })
        new_variables.append({
                "initial-value": size+1,
                "name": "y_max",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "initialized",
                "type": "int"
            })
        new_variables.append({
                "initial-value": 0,
                "name": "reset_goal",
                "type": "int"
            })

        

        data["automata"][0]["edges"]=edges
        data["variables"]=new_variables
        # print(replace_values(data,replacements))
        
        string_representation=json.dumps(data,ensure_ascii=False)
        for i in replacements:
            string_representation=string_representation.replace(str(i),f"\"{replacements[i]}\"")
        with open(f"{jani_folder}/{jani_file}_extended_jani.jani", "w", encoding="utf-8") as file:
            file.write(string_representation)
        with open(f"{jani_folder}/{jani_file}_extended_jani.jani") as f:
            data=json.load(f)
        with open(f"{jani_folder}/{jani_file}_extended_jani.jani","w",encoding="utf-8") as f:
            json.dump(data,f, ensure_ascii=False, indent=4)        

application_folder=os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "Application"
        )

evaluation_folder=os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "Evaluations"
    )

def replace_values(d, replacements):
    """
    Recursively replace values in a nested dictionary with their corresponding keys.
    """
    if isinstance(d, dict):
        return {k: replace_values(v, replacements) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_values(item, replacements) for item in d]
    return replacements.get(d, d)  # Replace value if it matches, otherwise return as is

def behaverify_comparison(experiment,initial_size,initial_seed):
    results={
        "behaverify":[],
        "PN_tina":[],
        "PN_storm":[],
        "nodes":[]
    }
    sizes=range(experiment["parameters"]["sizes"]["min"],experiment["parameters"]["sizes"]["max"],experiment["parameters"]["sizes"]["step"])
    seeds=range(experiment["parameters"]["seeds"]["min"],experiment["parameters"]["seeds"]["max"])
    files=["Unoptimized","Optimized"]
    jani_folder=f"{application_folder}/Outputs/JANI"
    model="behaverify"
    results={}

    skip = True

    for size,seed,file in product(sizes,seeds,files):
        
        if skip:
            if size == initial_size and seed == initial_seed:
                skip = False  # Found the resume point, start processing
                results[f"{size}"]={}
                results[f"{size}"]["behaverify"]={
                                                "result_optimized":[],
                                                "result_unoptimized":[],
                                                "user_time_optimized":[],
                                                "user_time_unoptimized":[],
                                                }
                results[f"{size}"]["storm"]={
                                                "result_optimized":[],
                                                "result_unoptimized":[],
                                                "user_time_optimized":[],
                                                "user_time_unoptimized":[],
                                                "min_trace_optimized":[],
                                                "max_trace_optimized":[],
                                                "min_trace_unoptimized":[],
                                                "max_trace_unoptimized":[]
                                                }
            else:
                continue

        print(size,seed,file)
        random.seed(seed)
        if file=="Unoptimized":
            if seed==experiment["parameters"]["seeds"]["min"]:
                results[f"{size}"]={}
                results[f"{size}"]["behaverify"]={
                                                "result_optimized":[],
                                                "result_unoptimized":[],
                                                "user_time_optimized":[],
                                                "user_time_unoptimized":[],
                                                }
                results[f"{size}"]["storm"]={
                                                "result_optimized":[],
                                                "result_unoptimized":[],
                                                "user_time_optimized":[],
                                                "user_time_unoptimized":[],
                                                "min_trace_optimized":[],
                                                "max_trace_optimized":[],
                                                "min_trace_unoptimized":[],
                                                "max_trace_unoptimized":[]
                                                }
                
            behaverify_results=beha.extract_data(size,seed)
            results[f"{size}"]["behaverify"]["result_optimized"].append(True if behaverify_results["optimized"]["specification"] == "true" else False)
            results[f"{size}"]["behaverify"]["result_unoptimized"].append(True if behaverify_results["unoptimized"]["specification"] == "true" else False)
            results[f"{size}"]["behaverify"]["user_time_optimized"].append(behaverify_results["optimized"]["user_time"])
            results[f"{size}"]["behaverify"]["user_time_unoptimized"].append(behaverify_results["unoptimized"]["user_time"])

        storm_verification_input={
            "metrics":"runtime_verification",
            "size":size,
            "seed":seed,
            "input_folder":f"{jani_folder}/{model}",
            "file":f"{file}_extended_jani.jani",
            "container_input":f"/home/{USER_behaverify}",
            "property":f"'P=? [F(reached_goal=3)]'",
            "output_folder":f"{evaluation_folder}/results/behaverify_comparison/storm_result/result_{size}",
            "label":file
        }

        prepare_jani(storm_verification_input["input_folder"],file,size,model)
   
        storm_results=btpn.storm_func(storm_verification_input)
        results[f"{size}"]["storm"][f"result_{file.lower()}"].append(True if storm_results["result"] == 1 else False)
        results[f"{size}"]["storm"][f"user_time_{file.lower()}"].append(storm_results["user_time"])
        results[f"{size}"]["storm"][f"min_trace_{file.lower()}"].append(storm_results["min_trace_length"])
        results[f"{size}"]["storm"][f"max_trace_{file.lower()}"].append(storm_results["max_trace_length"])
        if file=="Optimized":
            print(results)
    

    with open(f"{evaluation_folder}/results/behaverify_comparison/data.json", "w") as json_file:
        json.dump(results, json_file, indent=4)  # 'indent=4' makes it readable 

def dineros_composition(parameters,size,seed):
    # metric=parameters
    metrics="runtime_verification",
    size=size
    seed=seed
    file=experiments[1]["parameters"]["scenario"]
    btpn.dineros_func(metrics,size,seed,file)

def vacuum_cleaner(parameters):
    pass

experiments=[
    {
        "name":"behaverify_comparison",
        "function":behaverify_comparison,
        "parameters":{
            "sizes":{
                "min":10,
                "max":130,
                "step":10
            },
            "seeds":{
                "min":0,
                "max":50
            },
            "properties":[
                "P=? [F (x_pos=x_goal & y_pos=y_goal)]"
            ]
        },
        "model_checkers":["tina",[("storm","Optimized"),("storm","Unoptimized")],"nuxmv"]
    },
    {
        "name":"dineros_composition",
        "function":dineros_composition,
        "parameters":{
            "scenario":("dineros_grpn_original.pnml","")
        },
        "model_checkers":["tina","storm"]
    },
    {
        "name":"vacuum_cleaner",
        "function":vacuum_cleaner,
        "parameters":{
            "versions":[
                ("Application/Inputs/go_to_dock_groot.xml",""),
                ("Application/Inputs/big_bt_groot.xml","")
            ],
            "properties":[]
        },
        "model_checkers":["tina","storm"]
    }
]

def main():
    pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run BehaVerify evaluation")
    parser.add_argument("--size", type=int, required=True, help="Size of the evaluation model")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for evaluation")
    params=experiments[0]
    args = parser.parse_args()
    # experiments[0]["function"](params,args.size,args.seed)
    experiments[1]["function"](params,args.size,args.seed)