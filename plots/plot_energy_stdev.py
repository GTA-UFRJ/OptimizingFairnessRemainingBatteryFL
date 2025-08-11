import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","Uniform rounds","Prop. energy","Prop. time"]
stdev_soc_10_to_40 = [4464,4713,0,0]
stdev_soc_10_to_40_err = [68, 3,0,0]

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
ax.set_xlabel("Method")
ax.set_ylabel("Energy standard deviation")
ax.set_ylim(4000,5000)

plt.tight_layout()
plt.savefig("plots/stdev_soc.png", dpi=300)
plt.close()