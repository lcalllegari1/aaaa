import subprocess
import os

DATASETS_DIR = "datasets"
ITERATIONS = [1, 10, 100, 1000, 10000]
BLACKLIST = [
    "5000x2000",
    "10000x1000",
    "10000x5000",
    "10000x2000",
]


def runfw():
    for dataset in os.listdir(DATASETS_DIR):
        if dataset in BLACKLIST:
            continue
        for sparsity in sorted(os.listdir(os.path.join(DATASETS_DIR, dataset)), key=lambda x: float(x)):
            path = os.path.join(DATASETS_DIR, dataset, sparsity)
            for iteration_count in ITERATIONS:
                print(path, iteration_count)
                subprocess.run(["python3", "run.py", path, str(iteration_count)])

def runplotter():
    for dataset in os.listdir(DATASETS_DIR):
        if dataset in BLACKLIST:
            continue
        rows, cols = dataset.split("x")
        subprocess.run(["python3", "barplot.py", rows, cols])


runplotter()