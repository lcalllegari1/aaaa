import os 
import subprocess

from sys import argv

FRANK_WOLFE_ITERATIONS = 1000

FRANK_WOLFE_RESULTS = f"frank-wolfe{FRANK_WOLFE_ITERATIONS}.dat"
SIMPLEX_RESULTS = "simplex.dat"

DATASETS_DIR = "datasets"
RESULTS_DIR = "results"

def simplex(filepath): 
    return subprocess.run(["python3", "solver.py", filepath], capture_output=True, text=True).stdout

def frank_wolfe(filepath):
    return subprocess.run(["./solver", filepath, str(FRANK_WOLFE_ITERATIONS)], capture_output=True, text=True).stdout

def run(algorithm, dataset_path):
    results = ""
    for instance in sorted(os.listdir(dataset_path), key=lambda x: int(x)):
        filepath = os.path.join(dataset_path, instance, "csr_matrix.dat")
        results += algorithm(filepath)
    return results

def main(dataset_path):
    subprocess.run(["gcc", "solver.c", "-o", "solver", "-Ofast"])
    results_path = dataset_path.replace(DATASETS_DIR, RESULTS_DIR)
    os.makedirs(results_path, exist_ok=True)

    if not os.path.isfile(os.path.join(results_path, FRANK_WOLFE_RESULTS)):  
        with open(os.path.join(results_path, FRANK_WOLFE_RESULTS), "w") as file:
            file.write(run(frank_wolfe, dataset_path))

    if not os.path.isfile(os.path.join(results_path, SIMPLEX_RESULTS)):
        with open(os.path.join(results_path, SIMPLEX_RESULTS), "w") as file:
            file.write(run(simplex, dataset_path))

    with open(os.path.join(results_path, f"merged-results{FRANK_WOLFE_ITERATIONS}.dat"), "w") as file:
        simplex_results = open(os.path.join(results_path, SIMPLEX_RESULTS), "r")
        frank_wolfe_results = open(os.path.join(results_path, FRANK_WOLFE_RESULTS), "r")

        for simplex_line, frank_wolfe_line in zip(simplex_results, frank_wolfe_results):
            file.write(f"{simplex_line.strip()} {frank_wolfe_line}")

        simplex_results.close()
        frank_wolfe_results.close()

if __name__ == "__main__":
    if len(argv) != 2 and len(argv) != 3:
        print(f"Usage: $ python3 {argv[0]} <path> [<iterations>]")
    else:
        if len(argv) == 3:
            FRANK_WOLFE_ITERATIONS = argv[2]
            FRANK_WOLFE_RESULTS = f"frank-wolfe{FRANK_WOLFE_ITERATIONS}.dat"
        main(argv[1])
