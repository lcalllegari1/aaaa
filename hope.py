import subprocess

DATASETS_DIR = "datasets"

args = [
    "500x2000/0.9",
    "500x2000/0.925",
    "500x2000/0.975",
    "500x2000/0.99",
    "500x2000/0.95",
]

for arg in args:
    path = f"{DATASETS_DIR}/{arg}"
    subprocess.run(["python3", "run.py", path, "100000"])