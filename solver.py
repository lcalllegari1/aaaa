import numpy as np

from scipy.sparse import csr_matrix
from pyscipopt import Model, quicksum
from sys import argv

def solve(model):
    model.hideOutput()
    model.optimize()
    return model.getObjVal(), model.getSolvingTime()

def build_model(matrix, m, n):
    model = Model()
    x = [model.addVar(name=f"x_{j + 1}", vtype="C", lb=0) for j in range(n)]
    model.setObjective(quicksum(x[j] for j in range(n)), sense="minimize")
    for i in range(m):
        model.addCons(quicksum(matrix[i][j] * x[j] for j in range(n)) >= 1)
    return model

def main(filepath):
    with open(filepath, "r") as file:
        m, n, _ = map(int, file.readline().split())
        pointers = list(map(int, file.readline().split()))
        indices = list(map(int, file.readline().split()))
    matrix = csr_matrix((np.ones(len(indices)), indices, pointers), (m, n)).toarray()
    obj, time = solve(build_model(matrix, m, n))
    print(f"{obj:.6f} {time:.6f}")

if __name__ == "__main__":
    if len(argv) != 2:
        print(f"Usage: $ python3 {argv[1]} <filepath>")
    else:
        main(argv[1])