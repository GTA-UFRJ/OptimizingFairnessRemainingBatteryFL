import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('guiaraujo.mplstyle')

solvers = ["WF","FedAvg","PropEnerg","PropEffic"]
times_10_to_40 = [23.6, 12.91, 17.9, 14.7]
times_10_to_40_err = [0.1, 0.04, 0.2, 0.1]

x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))

# 10 to 40
rects = ax.bar(
    x, 
    times_10_to_40, 
    yerr=times_10_to_40_err,
    width=0.5, 
    label="SoC 10-40%")

ax.set_xticks(x)
ax.set_xticklabels(solvers)
ax.set_xlabel("Método")
ax.set_ylabel("Tempo da rodada (s)")
#ax.set_ylim(4000,5000)

plt.tight_layout()
plt.savefig("figures/round_time.png", dpi=300)
plt.close()