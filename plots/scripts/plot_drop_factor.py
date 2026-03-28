import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","FedAvg","PropEnerg","PropEffic"]
drop_factor_10_to_40 = [1.53, 1.79, 1.80, 1.79]
drop_factor_10_to_40_err = [0.02, 0.01, 0.01, 0.01]

x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))
# 10 to 40
rects = ax.bar(
    x, 
    drop_factor_10_to_40, 
    yerr=drop_factor_10_to_40_err,
    width=0.5, 
    label="SoC 10-40%")

ax.set_xticks(x)
ax.set_xticklabels(solvers)
ax.set_xlabel("Método")
ax.set_ylabel("FQ (%)")
ax.set_ylim(1,2)

plt.tight_layout()
plt.savefig("figures/drop_factor.png", dpi=300)
plt.close()