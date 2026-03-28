import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","FedAvg","PropEnerg","PropEffic"]
times_soc_10_to_40 = [1.565, 0.087, 0.097, 0.116]
times_soc_10_to_40_err = [0.030, 0.001, 0.001, 0.001]

x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))

# 10 to 40
rects = ax.bar(
    x, 
    times_soc_10_to_40, 
    yerr=times_soc_10_to_40_err,
    width=0.5, 
    label="SoC 10-40%")

ax.set_xticks(x)
ax.set_xticklabels(solvers)
ax.set_xlabel("Método")
ax.set_ylabel("Tempo para solução ($ms$)")
#ax.set_ylim(4000,5000)

plt.tight_layout()
plt.savefig("figures/solver_time.png", dpi=300)
plt.close()