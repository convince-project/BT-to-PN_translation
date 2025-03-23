import logging
import os
import re
from typing import List, Optional, Tuple
import docker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from instrumentation import Instrumentation

DOCKERFILE = "Dockerfile"
DOCKER_TAG_behaverify = "behaverify"
DOCKER_TAG_tina = "pnml_docker"


VENUE = "2025_CAV"
USER_behaverify = f"BehaVerify_{VENUE}"
USER_tina = "ubuntu_usr"

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


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
plt.style.use("bmh")



class tina_Instrumentation(Instrumentation):
    def __init__(self, metrics: List[str]):
        super().__init__(metrics, technology_name="tina")
        self.client: docker.DockerClient = docker.from_env()
        self.container: Optional[docker.models.containers.Container] = None

    # override
    def prepare(self):
        if not self.has_image():
            self.build_image()
        self.start_container()

    # override
    def run_experiment(self, parameters: dict) -> dict:
        assert "size" in parameters, "Size must be provided"
        size = parameters["size"]
        seed = parameters["seed"]
        file = parameters["file"]
        res = self.eval_with_size(size, seed,file)
        
        return res

    def build_image(self):
        repo_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Docker/ubuntu_20"
        )
        repo_folder = os.path.abspath(repo_folder)
        print(f"Building image from {repo_folder}")
        os.chdir(repo_folder)
        self.client.images.build(
            path=repo_folder,
            # dockerfile='REPRODUCIBILITY/2024_FMAS_SBT/Dockerfile',
            tag=DOCKER_TAG_tina,
            rm=True,
        )
        # for log in build_logs:
        #     if "stream" in log:
        #         logger.info(log["stream"].strip())
        #     if "error" in log:
        #         logger.error(log["error"].strip())

    def has_image(self):
        try:
            self.client.images.get(DOCKER_TAG_tina)
            return True
        except docker.errors.ImageNotFound:
            return False

    def start_container(self):
        assert self.has_image(), "Image must be built before starting container"
        existing_containers = self.client.containers.list(
            filters={"ancestor": DOCKER_TAG_tina}
        )
        assert len(existing_containers) <= 1, "There should be at most one container"
        if len(existing_containers) == 1:
            status = existing_containers[0].status
            logger.info(
                "Container %s exists with status %s", existing_containers[0].id, status
            )
            if status == "running":
                logger.info("Container is already running")
                self.container = existing_containers[0]
                return
            elif status == "exited":
                logger.info("Removing exited container")
                existing_containers[0].remove()
                existing_containers = []
        if len(existing_containers) == 0:
            logger.info("Creating new container")
            self.container = self.client.containers.run(
                DOCKER_TAG_tina,
                name=DOCKER_TAG_tina,
                detach=True,
                tty=True,
                user=USER_tina,
                # volumes={
                #     os.path.abspath(
                #         os.path.join(
                #             os.path.dirname(__file__),
                #             "..",
                #             "..",
                #             "..",
                #             "behaverify",
                #             "REPRODUCIBILITY",
                #             "2024_FMAS_SBT",
                #             "output",
                #         )
                #     ): {"bind": "/output", "mode": "rw"}
                # },
            )
        self.container.reload()
        status = self.container.status
        if status != "running":
            logger.info("Starting container")
            self.container.start()

    def stop_container(self):
        assert self.container is not None, "Container must be started before stopping"
        self.container.stop()
        self.container.remove()
        self.container = None

    def exec(self, commands: List[str]):
        assert (
            self.container is not None
        ), "Container must be started before executing commands"
        command = ";".join(commands)
        # print (f"Executing command: {command}")
        wrapped_cmd = f'bash -c "{command}"'
        er: docker.models.containers.ExecResult = self.container.exec_run(wrapped_cmd)
        return er.output.decode("utf-8")

    def eval_with_size(self, size: int, seed: int, file:str) -> dict:
        repr_folder = f"/home/{USER_tina}/"
        flattener_folder=f"/home/{USER_tina}/dineros/pnml-relast-tools/pnml-relast-flattener/build/libs"
        flattener_exec= f"pnml-relast-flattener-fatjar-0.2.jar"
        tina_path=f"/home/{USER_tina}/tina-3.7.0/bin/"
        
        output = self.exec(
            [
                f"sudo chmod -R a+w /home/{USER_tina}",
                f"ls /home/{USER_tina}/tina-3.7.0/bin ",
                f"{tina_path}walk -f safe -R -PNML {file} -v {repr_folder}inputs/PNMLs/log.txt",
            ]
        )
        results = {}
        print(output)
        # for metric in self.metrics:
        #     if metric == "runtime_verification":
        #         behaverify_fname = "SILENT_LTL_full_opt_simple_robot"
        #         output = self.exec(
        #             [f"cat {results_folder}/{behaverify_fname}_{size}.txt"]
        #         )
        #         # print(output)
        #         # find "User time    0.045 seconds" and extract the number
        #         matches = re.findall(r"User time\s+([0-9.]+) seconds", output)
        #         assert len(matches) == 1, f"Expected 1 match, got {matches}"
        #         results[metric] = float(matches[0])
        #     if metric == "runtime_conversion":
        #         results[metric] = 0.0
        return results

class dineros_Instrumentation(Instrumentation):
    def __init__(self, metrics: List[str]):
        super().__init__(metrics, technology_name="dineros")
        self.client: docker.DockerClient = docker.from_env()
        self.container: Optional[docker.models.containers.Container] = None

    # override
    def prepare(self):
        if not self.has_image():
            self.build_image()
        self.start_container()

    # override
    def run_experiment(self, parameters: dict) -> dict:
        assert "size" in parameters, "Size must be provided"
        size = parameters["size"]
        seed = parameters["seed"]
        file = parameters["file"]
        res = self.eval_with_size(size, seed,file)
        
        return res

    def build_image(self):
        repo_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Docker/ubuntu_20"
        )
        repo_folder = os.path.abspath(repo_folder)
        print(f"Building image from {repo_folder}")
        os.chdir(repo_folder)
        self.client.images.build(
            path=repo_folder,
            # dockerfile='REPRODUCIBILITY/2024_FMAS_SBT/Dockerfile',
            tag=DOCKER_TAG_tina,
            rm=True,
        )
        # for log in build_logs:
        #     if "stream" in log:
        #         logger.info(log["stream"].strip())
        #     if "error" in log:
        #         logger.error(log["error"].strip())

    def has_image(self):
        try:
            self.client.images.get(DOCKER_TAG_tina)
            return True
        except docker.errors.ImageNotFound:
            return False

    def start_container(self):
        assert self.has_image(), "Image must be built before starting container"
        existing_containers = self.client.containers.list(
            filters={"ancestor": DOCKER_TAG_tina}
        )
        assert len(existing_containers) <= 1, "There should be at most one container"
        if len(existing_containers) == 1:
            status = existing_containers[0].status
            logger.info(
                "Container %s exists with status %s", existing_containers[0].id, status
            )
            if status == "running":
                logger.info("Container is already running")
                self.container = existing_containers[0]
                return
            elif status == "exited":
                logger.info("Removing exited container")
                existing_containers[0].remove()
                existing_containers = []
        if len(existing_containers) == 0:
            logger.info("Creating new container")
            self.container = self.client.containers.run(
                DOCKER_TAG_tina,
                name=DOCKER_TAG_tina,
                detach=True,
                tty=True,
                user=USER_tina,
                # volumes={
                #     os.path.abspath(
                #         os.path.join(
                #             os.path.dirname(__file__),
                #             "..",
                #             "..",
                #             "..",
                #             "behaverify",
                #             "REPRODUCIBILITY",
                #             "2024_FMAS_SBT",
                #             "output",
                #         )
                #     ): {"bind": "/output", "mode": "rw"}
                # },
            )
        self.container.reload()
        status = self.container.status
        if status != "running":
            logger.info("Starting container")
            self.container.start()

    def stop_container(self):
        assert self.container is not None, "Container must be started before stopping"
        self.container.stop()
        self.container.remove()
        self.container = None

    def exec(self, commands: List[str]):
        assert (
            self.container is not None
        ), "Container must be started before executing commands"
        command = ";".join(commands)
        # print (f"Executing command: {command}")
        wrapped_cmd = f'bash -c "{command}"'
        er: docker.models.containers.ExecResult = self.container.exec_run(wrapped_cmd)
        return er.output.decode("utf-8")

    def eval_with_size(self, size: int, seed: int, file:str) -> dict:
        repr_folder = f"/home/{USER_tina}/"
        flattener_folder=f"/home/{USER_tina}/dineros/pnml-relast-tools/pnml-relast-flattener/build/libs"
        flattener_exec= f"pnml-relast-flattener-fatjar-0.2.jar"
        tina_path=f"/home/{USER_tina}/tina-3.7.0/bin/"
        output = self.exec(
            [
                f"sudo chmod -R a+w /home/{USER_tina}",
                f"sudo mkdir -p {repr_folder}/inputs/PNMLs/",
                f"test -e /home/{USER_tina}/inputs/GRPNs/{file} && echo 'File exists' || echo 'File does not exist'",
                f"java -jar {flattener_folder}/{flattener_exec} --help",
                f"java -jar {flattener_folder}/{flattener_exec} --pnml {repr_folder}inputs/GRPNs/{file} \
                    --tinaPath /home/{USER_tina}/ \
                    | tee /home/{USER_tina}/inputs/GRPNs/log.txt",
                f"FILE=$(ls -1 /home/{USER_tina}/temp/pnml | head -n 1)",
                f"time {tina_path}/tina -PNML /home/{USER_tina}/temp/pnml/$FILE >> {repr_folder}inputs/PNMLs/log.txt",
            ]
        )
        results = {}
        print(output)
        # for metric in self.metrics:
        #     if metric == "runtime_verification":
        #         behaverify_fname = "SILENT_LTL_full_opt_simple_robot"
        #         output = self.exec(
        #             [f"cat {results_folder}/{behaverify_fname}_{size}.txt"]
        #         )
        #         # print(output)
        #         # find "User time    0.045 seconds" and extract the number
        #         matches = re.findall(r"User time\s+([0-9.]+) seconds", output)
        #         assert len(matches) == 1, f"Expected 1 match, got {matches}"
        #         results[metric] = float(matches[0])
        #     if metric == "runtime_conversion":
        #         results[metric] = 0.0
        return results

class storm_Instrumentation(Instrumentation):
    def __init__(self, metrics: List[str]):
        super().__init__(metrics, technology_name="STORM")
        self.client: docker.DockerClient = docker.from_env()
        self.container: Optional[docker.models.containers.Container] = None

    # override
    def prepare(self):
        if not self.has_image():
            self.build_image()
        self.start_container()

    # override
    def run_experiment(self, parameters: dict) -> dict:
        assert "size" in parameters, "Size must be provided"
        res = self.eval_with_size(parameters)
        
        return res

    def build_image(self):
        repo_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Docker/ubuntu_22"
        )
        repo_folder = os.path.abspath(repo_folder)
        print(f"Building image from {repo_folder}")
        os.chdir(repo_folder)
        self.client.images.build(
            path=repo_folder,
            # dockerfile='REPRODUCIBILITY/2024_FMAS_SBT/Dockerfile',
            tag=DOCKER_TAG_behaverify,
            rm=True,
        )
        # for log in build_logs:
        #     if "stream" in log:
        #         logger.info(log["stream"].strip())
        #     if "error" in log:
        #         logger.error(log["error"].strip())

    def has_image(self):
        try:
            self.client.images.get(DOCKER_TAG_behaverify)
            return True
        except docker.errors.ImageNotFound:
            return False

    def start_container(self):
        assert self.has_image(), "Image must be built before starting container"
        existing_containers = self.client.containers.list(
            filters={"ancestor": DOCKER_TAG_behaverify}
        )
        assert len(existing_containers) <= 1, "There should be at most one container"
        if len(existing_containers) == 1:
            status = existing_containers[0].status
            logger.info(
                "Container %s exists with status %s", existing_containers[0].id, status
            )
            if status == "running":
                logger.info("Container is already running")
                self.container = existing_containers[0]
                return
            elif status == "exited":
                logger.info("Removing exited container")
                existing_containers[0].remove()
                existing_containers = []
        if len(existing_containers) == 0:
            logger.info("Creating new container")
            self.container = self.client.containers.run(
                DOCKER_TAG_behaverify,
                name=DOCKER_TAG_behaverify,
                detach=True,
                tty=True,
                user=USER_behaverify,
                # volumes={
                #     os.path.abspath(
                #         os.path.join(
                #             os.path.dirname(__file__),
                #             "..",
                #             "..",
                #             "..",
                #             "behaverify",
                #             "REPRODUCIBILITY",
                #             "2024_FMAS_SBT",
                #             "output",
                #         )
                #     ): {"bind": "/output", "mode": "rw"}
                # },
            )
        self.container.reload()
        status = self.container.status
        if status != "running":
            logger.info("Starting container")
            self.container.start()

    def stop_container(self):
        assert self.container is not None, "Container must be started before stopping"
        self.container.stop()
        self.container.remove()
        self.container = None

    def exec(self, commands: List[str]):
        assert (
            self.container is not None
        ), "Container must be started before executing commands"
        command = ";".join(commands)
        # print (f"Executing command: {command}")
        wrapped_cmd = f'bash -c "{command}"'
        er: docker.models.containers.ExecResult = self.container.exec_run(wrapped_cmd)
        return er.output.decode("utf-8")

    def eval_with_size(self, parameters) -> dict:
        size = parameters["size"]
        seed = parameters["seed"]
        file = parameters["file"]
        label= parameters["label"]
        property=parameters["property"]
        repr_folder = f"/home/{USER_behaverify}/"
        storm_exec= f"/home/{USER_behaverify}/smc_storm/bin/smc_storm"

        command = " ".join([
            "time smc_storm",
            f"--model {file}",
            f"--custom-property {property}",
            "--n-threads 10",
            "--batch-size 20",
            "--disable-explored-states-caching",
            "--show-statistics",
            f"--confidence 0.95"
        ])

        output = self.exec(
            [
                f"export PATH=$PATH:/home/{USER_behaverify}/smc_storm/bin",
                f"{command}"
            ]
        )
        print(output)
        results = output
        return results


def prepare_dineros_pnml():
    import xml.etree.ElementTree as ET
    translator_script=f"{application_folder}/Scripts/Translator.py"
    
    controllers={
        "L":{
            "controllerpage":"LeftControllerPage",
            "controller":"LeftController",
            "subnet":"LC1"
        },
        "R":{
            "controllerpage":"RightControllerPage",
            "controller":"RightController",
            "subnet":"RC1"
        }
    }
    
    origin_pn_folder = f"{evaluation_folder}/Support/"
    input_folder=dineros_pnml=f"{application_folder}/Inputs"
    dineros_pnml=os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "Application/Outputs/PNML/DiNeROS/"
        )
    params_file=f"{input_folder}/DiNeROS_nodes.xml"

    # Extract namespace from the root tag
    namespace = {"pnml": "http://www.pnml.org/version-2009/grammar/pnml"}

    PNML_tree=ET.parse(f"{origin_pn_folder}dineros_grpn_original.pnml")
    PNML_root=PNML_tree.getroot()

    for parameter in controllers.keys():
        

        # Load the XML file
        xml_file = params_file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        elements_additives=root.find(".//elements_additive")
        elements_additives.find(".//places").find(".//node").text=controllers[parameter]["controller"]
        elements_additives.find(".//places").find(".//subnet").text=controllers[parameter]["subnet"]
        elements_additives.find(".//transitions").find(".//node").text=controllers[parameter]["controller"]
        elements_additives.find(".//transitions").find(".//subnet").text=controllers[parameter]["subnet"]


        

        # Find the <side> element inside <constants>
        side_element = root.find(".//constants/side")

        # Modify the value if found
        if side_element is not None:
            side_element.set("value", parameter)  # Change "R" to "L"
        tree.write(xml_file, encoding="utf-8", xml_declaration=True)

        BT_file=f"{input_folder}/DiNeROS.xml"
        command=f"python3 {translator_script} --file {BT_file} --root R{parameter}"
        os.system(command)
        os.makedirs(f"{evaluation_folder}/results/pnml/",exist_ok=True)
        command=f"cp {dineros_pnml}Unoptimized_PN.xml {evaluation_folder}/results/pnml/Controller_{parameter}.pnml"
        os.system(command)

        tree =ET.parse(f"{evaluation_folder}/results/pnml/Controller_{parameter}.pnml")
        root = tree.getroot()
        print(f"{evaluation_folder}/results/pnml/Controller_{parameter}.pnml")
        # net_root=root.find(".//net")
        # Manually track parents
        for parent in root.iter():
            for graphics in list(parent):  # Iterate over children
                if graphics.tag == "graphics":
                    parent.remove(graphics)  # Remove element manually
        controller_element=PNML_root.find(f".//pnml:page[@id='{controllers[parameter]["controllerpage"]}']",namespace)
        elements = list(controller_element)  # Convert to a list
        for element in elements[1:]:  # Skip the first element
            controller_element.remove(element)
        # elements = list(net_root)  # Convert to a list
        # for element in elements:
        #     controller_element.append(element)
        
        for elem in tree.iter():
            if "}" in elem.tag:  # Namespace is present
                elem.tag = elem.tag.split("}", 1)[1]  # Remove namespace


        # Save the modified XML back to a file
        tree.write(f"{evaluation_folder}/results/pnml/Controller_{parameter}.pnml", encoding="utf-8", xml_declaration=True)
    for elem in PNML_root.iter():
        if "}" in elem.tag:  # Namespace is present
            elem.tag = elem.tag.split("}", 1)[1]  # Remove namespace
    PNML_tree.write(f"{evaluation_folder}/Support/dineros_grpn_BT.pnml", encoding="utf-8", xml_declaration=False)    
    os.path.abspath(dineros_pnml)
    os.chdir(dineros_pnml)

def prepare_input_file(container,file,folder):
    command=f"docker exec {container} mkdir -p {folder}"
    os.system(command)
    command = f"docker cp {file} {container}:{folder}"
    os.system(command)

def export_file(container,file,out_folder):
    command = f"docker cp  {container}:{file} {out_folder}"
    os.system(command)

def dineros_func(metrics,size,seed,file):    
    repo_folder = os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    origin_folder = os.path.abspath(repo_folder)+f"/Support/"
    result_folder = os.path.abspath(repo_folder)+f"/results/dineros_nets"
    repr_folder = f"/home/{USER_tina}/inputs/GRPNs"
    file="dineros_grpn_original.pnml"

    runner = dineros_Instrumentation(metrics)
    runner.prepare()
    prepare_input_file(runner.container.short_id,f"{origin_folder}{file}",repr_folder)
    results = runner.run_experiment({"size":size, "seed":seed, "file":file})
    print(repr_folder)
    export_file(runner.container.short_id,f"{repr_folder}/log.txt",repr_folder)
    export_file(runner.container.short_id,f"/home/{USER_tina}/temp/pnml",result_folder)
    
    prepare_dineros_pnml() 
    runner.stop_container()
    return results

def extract_smc_storm_results(log: str):
    result_pattern = re.search(r"Result:\s*(\d+)", log)
    user_time_pattern = re.search(r"real\s+(\d+)m([\d.]+)s", log)
    min_trace_pattern = re.search(r"Min trace length:\s*(\d+)", log)
    max_trace_pattern = re.search(r"Max trace length:\s*(\d+)", log)
    
    result = int(result_pattern.group(1)) if result_pattern else None
    
    if user_time_pattern:
        user_time = int(user_time_pattern.group(1)) * 60 + float(user_time_pattern.group(2))
    else:
        user_time = None
    
    min_trace_length = int(min_trace_pattern.group(1)) if min_trace_pattern else None
    max_trace_length = int(max_trace_pattern.group(1)) if max_trace_pattern else None
    
    return {
        "result": result,
        "user_time": user_time,
        "min_trace_length": min_trace_length,
        "max_trace_length": max_trace_length
    }

def storm_func(params):

    size=params["size"]
    seed=params["seed"]
    metrics=params["metrics"]
    input=f"{params["input_folder"]}/{params["file"]}"
    container_folder=f"{params["container_input"]}/"
    
    parameters={
        "size":size,
        "seed":seed,
        "file":f"{container_folder}inputs/{params['label']}/{params["file"]}",
        "property":params["property"],
        "label":params["label"]
    }
    print(container_folder)

    runner = storm_Instrumentation(metrics)
    runner.prepare()
    prepare_input_file(runner.container.short_id,input,f"{container_folder}inputs/{parameters['label']}")
    results = runner.run_experiment(parameters)
    os.makedirs(f"{params["output_folder"]}/{params["label"]}",exist_ok=True)

    result_struct=extract_smc_storm_results(results)

    # docker cp my_container:/home/user/data.txt /home/matt/Desktop/
    runner.stop_container()
    return result_struct
    
def tina_func(metrics,size,seed):
    file="behaverify"

    command=f"python3 {application_folder}/Scripts/Translator.py --file {application_folder}/Inputs/{file}.xml"
    os.system(command)
    repr_folder = f"/home/{USER_tina}/inputs/PNMLs"
    input_folder=f"{application_folder}/Outputs/PNML/{file}"
    file=f"Unoptimized_PN.xml"
    outfile=f"Unoptimized_PN.pnml"
    command = f"docker cp {input_folder}/{file} {runner.container.short_id}:{repr_folder}/{outfile}"
    os.system(command)
    runner = tina_Instrumentation(metrics)
    runner.prepare()
    
    
    results = runner.run_experiment({"size":size, "seed":seed,"file":f"{repr_folder}/{outfile}"})
    # docker cp my_container:/home/user/data.txt /home/matt/Desktop/
    
    origin_folder = os.path.abspath(evaluation_folder)+f"/Support/log.txt"
    command = f"docker cp  {runner.container.short_id}:{repr_folder}/log.txt {origin_folder}"
    os.system(command)
    
    runner.stop_container()
    return results

def extract_data(size=10,seed=0):
    
    metrics = [
        "runtime_verification",
        # "runtime_conversion",
    ]
    results=None
    jani_folder=f"{application_folder}/Outputs/JANI"
    model="behaverify"
    file="Optimized_jani"

    strom_verification_input={
        "metrics":metrics,
        "size":size,
        "seed":seed,
        "input_folder":f"{jani_folder}/{model}",
        "file":f"{file}.jani",
        "container_input":f"/home/{USER_behaverify}/inputs",
        "output_folder":"",
        "property":"'P=? [F(x_pos=111 & y_pos=1)]'",
        "output_folder":f"{evaluation_folder}/results/behaverify_comparison/storm_result"
    }

    results=storm_func(strom_verification_input)


    # results=dineros_func(metrics,10,0)
    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BehaVerify evaluation")
    parser.add_argument("--size", type=int, required=True, help="Size of the evaluation model")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for evaluation")

    args = parser.parse_args()
    results=extract_data(args.size,args.seed)
    print("BehaVerify Results:", results)