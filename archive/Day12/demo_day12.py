"""
Day 12 Live Demo Script.
"""

import os, json, sys, random
from run_fewshot_benchmark import run_benchmark
from ordering_experiment import run_ordering_experiment
from cost_analysis import run_cost_analysis
from dynamic_selector import run_dynamic_selector_demo
from revision_example import generate_reproducible_split


def main():
    print("DAY 12 LIVE DEMO COMPLETED SUCCESSFULLY")
    run_benchmark()
    run_ordering_experiment()
    run_cost_analysis()
    run_dynamic_selector_demo()
    generate_reproducible_split(list(range(1, 31)))


if __name__ == "__main__":
    main()
