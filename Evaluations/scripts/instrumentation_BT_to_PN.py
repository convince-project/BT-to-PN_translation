import logging
import os
import re
from typing import List, Optional, Tuple
import docker
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from instrumentation import Instrumentation

def extract_data(size,seed):
    pass

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run BehaVerify evaluation")
    parser.add_argument("--size", type=int, required=True, help="Size of the evaluation model")
    parser.add_argument("--seed", type=int, required=True, help="Random seed for evaluation")

    args = parser.parse_args()
    results=extract_data(args.size,args.seed)
    print("BehaVerify Results:", results)