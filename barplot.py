import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib

from sys import argv

matplotlib.use('TkAgg')

# Enable LaTeX text rendering
plt.rc('text', usetex=True)

# Set LaTeX font to Computer Modern
plt.rc('font', family='serif', serif=['Computer Modern Roman'])

plt.rcParams['font.size'] = 14          # Default font size
plt.rcParams['axes.titlesize'] = 16     # Font size for axes titles
plt.rcParams['axes.labelsize'] = 14     # Font size for x and y labels
plt.rcParams['xtick.labelsize'] = 12    # Font size for x-tick labels
plt.rcParams['ytick.labelsize'] = 12    # Font size for y-tick labels
plt.rcParams['legend.fontsize'] = 10    # Font size for legend

ROWS, COLS = argv[1], argv[2]
RESULTS_DIR = "results"
PATH = f"{RESULTS_DIR}/{ROWS}x{COLS}"
TITLE = rf"{ROWS}$\times${COLS}"

ITERATIONS = [
    10000, 
    1000, 
    100
]
TIME_FACTOR = 1e3
LABELS = {
    1: "seconds",
    1e3: "milliseconds",
    1e6: "microseconds",
    1e9: "nanoseconds"
}

FW_COLORS = {
    10000: "#33CA7F",
    1000: "#8B80F9",
    100: "#F64740",
    # ITERATIONS[3]: "red",
}

sparsity_levels = []
optimal_values = []
lower_bounds = {}
upper_bounds = {}
simplex_times = []
frank_wolfe_times = {}

def read(path):
    for iteration_count in ITERATIONS:
        lower_bounds[iteration_count] = []
        upper_bounds[iteration_count] = []
        frank_wolfe_times[iteration_count] = []
    for sparsity in sorted(os.listdir(path), key=lambda x: float(x)):
        sparsity_levels.append(f"{float(sparsity):.3f}")
        dataset_path = os.path.join(path, sparsity)
        with open(os.path.join(dataset_path, "simplex.dat"), "r") as file:
            a, b = [], []
            for line in file:
                values = list(map(float, line.split()))
                a.append(values[0]) # opt
                b.append(values[1]) # time
            optimal_values.append(a)
            simplex_times.append(b)
        for iteration_count in ITERATIONS:
            filename = f"frank-wolfe{iteration_count}.dat"
            with open(os.path.join(dataset_path, filename), "r") as file:
                a, b, c = [], [], []
                for line in file:
                    values = list(map(float, line.split()))
                    a.append(values[0])  # lb
                    b.append(values[1])  # ub
                    c.append(values[2])  # time
                lower_bounds[iteration_count].append(a)
                upper_bounds[iteration_count].append(b)
                frank_wolfe_times[iteration_count].append(c)

def barplot():
    bar_width = 0.35
    indices = np.arange(len(sparsity_levels))
    plt.figure(figsize=(5, 4))

    for i in range(len(simplex_times)):
        simplex_times[i].remove(max(simplex_times[i]))
        simplex_times[i].remove(min(simplex_times[i]))

    plt.bar(
        indices - bar_width / 2, 
        [np.mean(simplex_times[i]) * TIME_FACTOR for i in range(len(simplex_times))], 
        bar_width, label="Simplex", 
        #yerr=[np.std(simplex_times[i]) * TIME_FACTOR for i in range(len(simplex_times))], 
        capsize=5,
        color="#247BA0"
    )

    lb_means = {iteration_count: [np.mean(lower_bounds[iteration_count][i]) / np.mean(optimal_values[i]) for i in range(len(sparsity_levels))] for iteration_count in ITERATIONS}
    ub_means = {iteration_count: [np.mean(upper_bounds[iteration_count][i]) / np.mean(optimal_values[i]) for i in range(len(sparsity_levels))] for iteration_count in ITERATIONS}


    with open(f"timedata/{ROWS}x{COLS}.dat", "w") as file:
        sparsity_str = " ".join(sparsity for sparsity in sparsity_levels)
        file.write(f"{sparsity_str}\n")
        for iteration_count in ITERATIONS:
            lb_values = lb_means[iteration_count]
            ub_values = ub_means[iteration_count]
            time_values = [np.mean(frank_wolfe_times[iteration_count][i]) for i in range(len(sparsity_levels))]
            simplex_values = [np.mean(simplex_times[i]) for i in range(len(simplex_times))]
            lb_str = " ".join(f"{value:.6f}" for value in lb_values)
            ub_str = " ".join(f"{value:.6f}" for value in ub_values)
            time_str = " ".join(f"{value:.6f}" for value in time_values)
            simplex_str = " ".join(f"{value:.6f}" for value in simplex_values)
            file.write(f"{iteration_count}:{lb_str}|{ub_str}|{time_str}|{simplex_str}\n")

    with open(f"timedata2/{ROWS}x{COLS}.dat", "w") as file:
        for i, sparsity in enumerate(sparsity_levels):
            line = f"& {sparsity} & "
            line += " & ".join(f"{lb_means[iteration_count][i]:.4f}" for iteration_count in reversed(ITERATIONS)) + " & "
            line += " & ".join(f"{ub_means[iteration_count][i]:.4f}" for iteration_count in reversed(ITERATIONS)) + " & "
            line += " & ".join([f"{np.mean(frank_wolfe_times[iteration_count][i]) * TIME_FACTOR:.4f}" for iteration_count in reversed(ITERATIONS)]) + f" & {np.mean(simplex_times[i]) * TIME_FACTOR:.4f} \\\\\n"
            file.write(line)

    #print(lb_means)
    #print(ub_means)

    for iteration_count in ITERATIONS:
        plt.bar(
            indices + bar_width / 2,
            [np.mean(frank_wolfe_times[iteration_count][i]) * TIME_FACTOR for i in range(len(sparsity_levels))],
            bar_width, label=f"Frank-Wolfe ({iteration_count} iterations)",
            color = FW_COLORS[iteration_count],
            #yerr=[np.std(frank_wolfe_times[iteration_count][i]) * TIME_FACTOR for i in range(len(sparsity_levels))],
            capsize=5,
        )

    plt.xticks(indices, sparsity_levels)
    plt.ylabel(f"Execution Time ({LABELS[TIME_FACTOR]})")
    plt.xlabel("Sparsity")
    plt.legend()
    plt.title(TITLE)
    plt.tight_layout()
    plt.savefig(f"barplots/{ROWS}x{COLS}.pdf")
    # plt.show()

# read(PATH)
read(PATH) # for the automated script
barplot()