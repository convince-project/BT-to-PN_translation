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
DOCKER_TAG = "behaverify"
VENUE = "2025_CAV"
USER = f"BehaVerify_{VENUE}"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
plt.style.use("bmh")


class BehaverifyInstrumentation(Instrumentation):
    def __init__(self, metrics: List[str]):
        super().__init__(metrics, technology_name="Behaverify")
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
        res = self.eval_with_size(size, seed)
        for metric in self.metrics:
            assert metric in res, f"{metric} must be in the results {res}"
        return res

    def build_image(self):
        repo_folder = os.path.join(
            os.path.dirname(__file__),
            "..",
            "Docker/behaverify"
        )
        repo_folder = os.path.abspath(repo_folder)
        print(f"Building image from {repo_folder}")
        os.chdir(repo_folder)
        self.client.images.build(
            path=repo_folder,
            # dockerfile='REPRODUCIBILITY/2024_FMAS_SBT/Dockerfile',
            tag=DOCKER_TAG,
            rm=True,
        )
        # for log in build_logs:
        #     if "stream" in log:
        #         logger.info(log["stream"].strip())
        #     if "error" in log:
        #         logger.error(log["error"].strip())

    def has_image(self):
        try:
            self.client.images.get(DOCKER_TAG)
            return True
        except docker.errors.ImageNotFound:
            return False

    def start_container(self):
        assert self.has_image(), "Image must be built before starting container"
        existing_containers = self.client.containers.list(
            filters={"ancestor": DOCKER_TAG}
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
                DOCKER_TAG,
                name=DOCKER_TAG,
                detach=True,
                tty=True,
                user=USER,
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

    def eval_with_size(self, size: int, seed: int) -> dict:
        repr_folder = f"/home/{USER}/behaverify/REPRODUCIBILITY/{VENUE}"
        example_folder = f"{repr_folder}/examples/simple_robot"
        python_bin = f"/home/{USER}/python_venvs/behaverify/bin/python3"
        tree_folder = f"{example_folder}/tree"
        smv_folder = f"{example_folder}/smv"
        results_folder = f"{example_folder}/results"
        output = self.exec(
            [
                f"cd {repr_folder}",
                "pwd",
                f"cd {repr_folder}/examples",
                "./clean_all.sh",
                "echo '>>>> make_tree.py'",
                f"mkdir -p {tree_folder}",
                f"cd {example_folder}",
                f"{python_bin} make_tree.py {example_folder} {tree_folder} {size} {size} 2",
                "echo '>>>> ls'",
                f"ls {tree_folder}",
                # "echo '>>>> cat CHANGED_simple_robot_10.tree'",
                # f"cat {tree_folder}/CHANGED_simple_robot_10.tree",
                # f"echo '>>>> cat simple_robot_{size}.tree'",
                # f"cat {tree_folder}/simple_robot_{size}.tree",
                # "echo '>>>> diff CHANGED_simple_robot_10.tree simple_robot_10.tree'",
                # f"diff {tree_folder}/CHANGED_simple_robot_10.tree {tree_folder}/simple_robot_10.tree",
                f"mkdir -p {smv_folder}",
                f"cd {repr_folder}/scripts/build_scripts",
                "echo '>>>> pwd'",
                "pwd",
                "echo '>>>> make_optimized_smv.sh'",
                f"./make_optimized_smv.sh {python_bin} {example_folder} simple_robot_{size}",
                # f"./make_full_opt_smv.sh {python_bin} {example_folder} CHANGED_simple_robot_{size}",
                f"echo '>>>> ls {smv_folder}'",
                f"ls {smv_folder}",
                # "echo '>>>> cat full_opt_simple_robot_XXX.smv'",
                # f"cat {smv_folder}/full_opt_simple_robot_{size}.smv",
                "echo '>>>> exp_simple_robot_run.sh'",
                f"mkdir -p {results_folder}",
                f"cd {repr_folder}/scripts/encoding_timing_scripts",
                f"echo {seed} > /tmp/nuXmv_seed",
                f"./exp_simple_robot_run.sh {size} {size} 2",
                "echo '>>>> ls'",
                f"ls {results_folder}",
                # "echo '>>>> tail LTL_full_opt_CHANGED_simple_robot'",
                # f"tail -n 1 {results_folder}/LTL_full_opt_CHANGED_simple_robot_{size}.txt",
                "echo '>>>> tail LTL_full_opt_simple_robot'",
                f"tail -n 1 {results_folder}/LTL_full_opt_simple_robot_{size}.txt",
                # "echo '>>>> tail SILENT_LTL_full_opt_CHANGED_simple_robot'",
                # f"tail -n 27 {results_folder}/SILENT_LTL_full_opt_CHANGED_simple_robot_{size}.txt",
                "echo '>>>> tail SILENT_LTL_full_opt_simple_robot'",
                f"tail -n 27 {results_folder}/SILENT_LTL_full_opt_simple_robot_{size}.txt",
            ]
        )
        print(output)
        results = {}
        # print(output)
        for metric in self.metrics:
            if metric == "runtime_verification":
                behaverify_fname = "SILENT_LTL_full_opt_simple_robot"
                output = self.exec(
                    [f"cat {results_folder}/{behaverify_fname}_{size}.txt"]
                )
                # print(output)
                # find "User time    0.045 seconds" and extract the number
                matches = re.findall(r"User time\s+([0-9.]+) seconds", output)
                assert len(matches) == 1, f"Expected 1 match, got {matches}"
                results[metric] = float(matches[0])
            if metric == "runtime_conversion":
                results[metric] = 0.0
        return results

def extract_data(size=10,seed=0):
    metrics = [
        "runtime_verification",
        # "runtime_conversion",
    ]
    runner = BehaverifyInstrumentation(metrics)
    runner.prepare()
    results = runner.run_experiment({"size":size, "seed":seed})
    
    
    # Define source and destination paths
    repr_folder = f"/home/{USER}/behaverify/REPRODUCIBILITY/{VENUE}"
    example_folder = f"{repr_folder}/examples/simple_robot"

    result_path = f"{example_folder}/results"
    tree_folder = f"{example_folder}/tree"
    smv_folder = f"{example_folder}/smv"

    repo_folder = os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    
    destination_path = os.path.abspath(repo_folder)+f"/results/results_{args.size}/"
    os.makedirs(destination_path,exist_ok=True)
    # Construct the `docker cp` command
    command = f"docker cp {runner.container.short_id}:{result_path} {destination_path}"
    os.system(command)
    command = f"docker cp {runner.container.short_id}:{tree_folder} {destination_path}"
    os.system(command)
    command = f"docker cp {runner.container.short_id}:{smv_folder} {destination_path}"
    os.system(command)

    # Run the command on the host using os.system() or subprocess.run()
    os.system(command)  # Alternative: subprocess.run(command, shell=True)
    command=f"rm {destination_path}results/*_first_* {destination_path}results/*_last_* \
                 {destination_path}smv/first_* {destination_path}smv/last_*  "
    os.system(command)
    # docker cp my_container:/home/user/data.txt /home/matt/Desktop/
    runner.stop_container()

    
    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BehaVerify evaluation")
    parser.add_argument("--size", type=int, required=True, help="Size of the evaluation model")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for evaluation")

    args = parser.parse_args()
    results=extract_data(args.size,args.seed)
    print("BehaVerify Results:", results)