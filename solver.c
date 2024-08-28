#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#define MAX_ROWS 10000
#define MAX_COLS 10000
#define MAX_SIZE MAX_ROWS * MAX_COLS

typedef struct {
    int indices[MAX_SIZE];
    int pointers[MAX_ROWS + 1];
} csr_matrix;

csr_matrix A, T;

int m = MAX_ROWS;
int n = MAX_COLS;

int nnz = MAX_SIZE;

void read(const char * const path) {
    FILE * file = fopen(path, "r");
    int t;

    t = fscanf(file, "%d %d %d", &m, &n, &nnz);

    for (int i = 0; i <= m; i++) 
        t = fscanf(file, "%d", A.pointers + i);
    for (int i = 0; i < nnz; i++)
        t = fscanf(file, "%d", A.indices + i);
    for (int i = 0; i <= n; i++) 
        t = fscanf(file, "%d", T.pointers + i);
    for (int i = 0; i < nnz; i++)
        t = fscanf(file, "%d", T.indices + i);

    fclose(file);
}


int row_start(const csr_matrix * const matrix, int row) {
    return matrix->pointers[row];
}

int row_end(const csr_matrix * const matrix, int row) {
    return matrix->pointers[row + 1];
}

void starting_u(double * const u) {
    for (int i = 0; i < m; i++) {
        u[i] = 1;
    }
}

double L(const double * const u, uint8_t * const x) {
    double objective = 0;

    for (int j = 0; j < n; j++) {
        double result = 0;
        for (int i = row_start(&T, j); i < row_end(&T, j); i++) {
            result += u[T.indices[i]];
        }
        if (x[j] = (result > 1)) {
            objective += (1 - result);
        }
    }

    for (int i = 0; i < m; i++) {
        objective += u[i];
    }
    
    return objective;
}

void subgradient(const uint8_t * const x, int * const s) {
    for (int i = 0; i < m; i++) {
        s[i] = 1;
        for (int j = row_start(&A, i); j < row_end(&A, i); j++) {
            s[i] -= x[A.indices[j]];
        }
    }
}

void argmax(const int * const s, uint8_t * const d) {
    for (int i = 0; i < m; i++) {
        d[i] = (s[i] > 0);
    }
}

void next_u(double * const u, const uint8_t * const d, double gamma) {
    for (int i = 0; i < m; i++) {
        u[i] += gamma * (d[i] - u[i]);
    }
}

void update_lower_bound(double * const lower_bound, double candidate) {
    if (candidate > *lower_bound) {
        *lower_bound = candidate;
    }
}

void update_upper_bound(double * const upper_bound, double objective,
    const int * const s, const uint8_t * const d, const double * const u
) {
    double candidate = objective;
    for (int i = 0; i < m; i++) {
        candidate += s[i] * (d[i] - u[i]);
    }

    if (candidate < *upper_bound) {
        *upper_bound = candidate;
    }
}

void solve(int K) {
    double u[m], objective, lower_bound = 0, upper_bound = 1e9;
    int s[m]; uint8_t d[m], x[n];

    clock_t start = clock();
    starting_u(u);
    for (int k = 0; k < K; k++) {
        objective = L(u, x);
        subgradient(x, s);
        argmax(s, d);
        update_lower_bound(&lower_bound, objective);
        update_upper_bound(&upper_bound, objective, s, d, u);
        next_u(u, d, 2 / ((double) k + 2));
    }
    clock_t end = clock();
    printf("%f %f %f\n", lower_bound, upper_bound, ((double) (end - start)) / CLOCKS_PER_SEC);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        printf("Usage: $ %s <path> <K>\n", argv[0]);
        return 0;
    }

    read(argv[1]);
    solve(atoi(argv[2]));
}