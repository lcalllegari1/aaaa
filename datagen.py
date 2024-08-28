import os
import numpy as np

from sys import argv
from scipy.sparse import csr_matrix

DATASETS_DIR = "datasets"

def generate_matrix(rows, cols, sparsity):
    nnz = int(round((1 - sparsity) * rows * cols))
    matrix = np.zeros((rows, cols), dtype=int)

    for r in range(rows):
        matrix[r, np.random.choice(cols)] = 1

    nc = np.where(matrix.sum(axis=0) == 0)[0]
    for c in nc:
        matrix[np.random.choice(rows), c] = 1

    remaining_nnz = nnz - np.sum(matrix)
    if remaining_nnz > 0:
        zeros = np.argwhere(matrix == 0)
        selected_indices = zeros[
            np.random.choice(zeros.shape[0], remaining_nnz, False)
        ]
        for r, c in selected_indices:
            matrix[r, c] = 1

    print(f"generated matrix: {rows}x{cols}, nnz: {nnz}, specified sparsity: {sparsity:.3f}, max sparsity: {1 - rows / (rows * cols):.3f} , actual sparsity: {1 - np.count_nonzero(matrix) / float(np.prod(matrix.shape)):.3f}")   
    return csr_matrix(matrix)

def save(matrix, path):
    header = f"{matrix.shape[0]} {matrix.shape[1]} {matrix.nnz}\n"
    pointers = " ".join(map(str, matrix.indptr)) + "\n"
    indices = " ".join(map(str, matrix.indices)) + "\n"
    buffer = f"{header}{pointers}{indices}"
    pointers = " ".join(map(str, matrix.transpose().tocsr().indptr)) + "\n"
    indices = " ".join(map(str, matrix.transpose().tocsr().indices)) + "\n"
    buffer += f"{pointers}{indices}"
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "csr_matrix.dat"), "w") as file:
        file.write(buffer)

def generate_dataset(size, rows, cols, sparsity):
    path = f"{DATASETS_DIR}/{rows}x{cols}/{sparsity}/"
    for i in range(size):
        save(generate_matrix(rows, cols, sparsity), os.path.join(path, f"{i + 1}"))

def main(size, rows, cols, sparsity):
    generate_dataset(size, rows, cols, sparsity)

if __name__ == "__main__":
    if len(argv) != 5:
        print(f"Usage: $ python3 {argv[0]} <size> <rows> <cols> <sparsity>")
    else:
        main(int(argv[1]), int(argv[2]), int(argv[3]), float(argv[4]))