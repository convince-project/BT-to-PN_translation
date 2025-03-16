from typing import List, Optional


class Instrumentation:
    """A module to manage the execution of a technology to be evaluated.
    It supports starting and stopping the technology, as well as
    evaluating metrics."""
    def __init__(self, metrics: List[str], technology_name: str):
        # Name of the technology to be evaluated, must be set by the subclass
        self.technology_name = technology_name
        # List of metrics to be evaluated
        self.metrics = metrics
        # Default parameters in case they are not provided
        self.default_parameters = {
            "size": 10,
            "seed": 0,
            "confidence": 0.95,
        }

    def prepare(self):
        """Prepare the technology for evaluation.
        To be executed once for all experiments."""
        raise NotImplementedError

    def run_experiment(self, parameters: dict):
        """Run an experiment with the given parameters.
        Must return a dictionary with one result per metric."""
        raise NotImplementedError

    def __str__(self):
        return self.technology_name
