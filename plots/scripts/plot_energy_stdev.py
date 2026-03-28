import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","FedAvg","PropEnerg","PropEffic"]
stdev_soc_10_to_40 = [6385,6751,6612,6733]
stdev_soc_10_to_40_err = [67, 66, 79, 65]

x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))

# 10 to 40
rects = ax.bar(
    x, 
    stdev_soc_10_to_40, 
    yerr=stdev_soc_10_to_40_err,
    width=0.5, 
    label="SoC 10-40%")

ax.set_xticks(x)
ax.set_xticklabels(solvers)
ax.set_xlabel("Método")
ax.set_ylabel("Desvio padrão da energia")
ax.set_ylim(6000,7000)

plt.tight_layout()
plt.savefig("plots/stdev_soc.png", dpi=300)
plt.close()