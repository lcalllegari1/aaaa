import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os

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
plt.rcParams['legend.fontsize'] = 12    # Font size for legend

sizes = {
    "xs": (4, 4, 0.2, 40),
    "small": (5, 4, 0.2, 40),
    "normal": (8, 4, 0.1, 35),
}

FRANK_WOLFE_ITERATIONS = 100000

RESULTS_DIR = "results"
PLOTS_DIR = "plots"
PLOTDATA_DIR = "plotsdata"
FILENAME = f"merged-results{FRANK_WOLFE_ITERATIONS}.dat"

ROWS, COLS = argv[1], argv[2]
SIZE = f"{ROWS}x{COLS}"
TITLE = rf"{ROWS}$\times${COLS}"

PATH = f"{RESULTS_DIR}/{SIZE}"

sparsity_levels = []
optimal_values = []
lower_bounds = []
upper_bounds = []
simplex_times = []
frank_wolfe_times = []

def read(path):
    for sparsity in sorted(os.listdir(path), key=lambda x: float(x)):
        sparsity_levels.append(f"{float(sparsity):.3f}")
        dataset_path = os.path.join(path, sparsity)
        with open(os.path.join(dataset_path, FILENAME), "r") as file:
            a, b, c, d, e = [], [], [], [], []
            for line in file:
                values = list(map(float, line.split()))
                a.append(values[0])  # objective value
                b.append(values[1])  # simplex time
                c.append(values[2])  # lower bound
                d.append(values[3])  # upper bound
                e.append(values[4])  # frank-wolfe time
            optimal_values.append(a)
            simplex_times.append(b)
            lower_bounds.append(c)
            upper_bounds.append(d)
            frank_wolfe_times.append(e)

def plot(size):
    width, height, offset, xtickwidth = sizes[size]
    plt.figure(figsize=(width, height))

    colors = ['#1F77B4', '#2CA02C', '#FA7921']  # blue, green, orange
    markers = ['^', 'o', 'v']

    has_to_write = False if os.path.isfile(os.path.join(PLOTDATA_DIR, f"{SIZE}.dat")) else True

    for i in range(len(sparsity_levels)):
        sparsity = sparsity_levels[i]

        optimal_values_mean = np.mean(optimal_values[i])
        optimal_values_std = np.std(optimal_values[i])

        lower_bounds_mean = np.mean(lower_bounds[i])
        lower_bounds_std = np.std(lower_bounds[i])

        upper_bounds_mean = np.mean(upper_bounds[i])
        upper_bounds_std = np.std(upper_bounds[i])

        lower_bounds_norm = lower_bounds_mean / optimal_values_mean
        upper_bounds_norm = upper_bounds_mean / optimal_values_mean
        lower_bounds_std_norm = lower_bounds_std / optimal_values_mean
        upper_bounds_std_norm = upper_bounds_std / optimal_values_mean
        optimal_values_std_norm = optimal_values_std / optimal_values_mean

        
        if has_to_write:
            os.makedirs(PLOTDATA_DIR, exist_ok=True)
            with open(f"{PLOTDATA_DIR}/{SIZE}.dat", "a") as file:
                #line = f"{sparsity} {optimal_values_mean:.3f} {optimal_values_std:.3f} {lower_bounds_mean:.3f} {lower_bounds_std:.3f} {lower_bounds_norm:.3f} {upper_bounds_mean:.3f} {upper_bounds_std:.3f} {upper_bounds_norm:.3f}\n"
                line = f"{sparsity} {TITLE} & {lower_bounds_norm:.3f} & {upper_bounds_norm:.3f} \\\\\n"
                file.write(line)

        plt.errorbar(i - offset, lower_bounds_norm, yerr=lower_bounds_std_norm, fmt=markers[0], color=colors[0], capsize=5, lw=1, label="Lower Bound" if i == 0 else "", markersize=7)
        plt.errorbar(i, 1, yerr=optimal_values_std_norm, fmt=markers[1], color=colors[1], capsize=5, lw=1, label="Optimal Value" if i == 0 else "", markersize=7)
        plt.errorbar(i + offset, upper_bounds_norm, yerr=upper_bounds_std_norm, fmt=markers[2], color=colors[2], capsize=5, lw=1, label="Upper Bound" if i == 0 else "", markersize=7)

    handles, labels = plt.gca().get_legend_handles_labels()
    order = [2, 1, 0]  
    plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='best')

    plt.xlabel("Sparsity")
    plt.ylabel("Normalized Values")

    plt.xticks(np.arange(len(sparsity_levels)), labels=sparsity_levels)
    plt.tick_params(axis='x', which='both', length=2, width=xtickwidth, colors='black', direction='inout', pad=10)
    plt.grid(True, axis="y")
    plt.title(TITLE)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, f"{SIZE}-{size}.pdf"))
    #plt.show()

read(PATH)
plot(argv[3] if len(argv) == 4 else "small")
