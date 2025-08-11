import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","Uniform rounds","Prop. energy","Prop. time"]
stdev_soc_8_to_10 = [375,334,0,0]
stdev_soc_8_to_10_err = [92, 3,0,0]
stdev_soc_10_to_40 = [4464,4713,0,0]
stdev_soc_10_to_40_err = [68, 3,0,0]


x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9), layout='constrained')

# 8 to 10
rects = ax.bar(
    x, 
    stdev_soc_8_to_10, 
    yerr=stdev_soc_8_to_10_err,
    width=0.25, 
    label="SoC 8-10%")
ax.bar_label(rects, padding=3)

# 10 to 40
rects = ax.bar(
    x+0.25, 
    stdev_soc_10_to_40, 
    yerr=stdev_soc_10_to_40_err,
    width=0.25, 
    label="SoC 10-40%")
ax.bar_label(rects, padding=3)

ax.set_xticks(x+0.25/2)
ax.set_xticklabels(solvers)
ax.set_xlabel("Method")
ax.set_ylabel("Energy drop factor (%)")
ax.set_ylim(4000,5000)

ax.legend()

plt.tight_layout()
plt.savefig("plots/stdev_soc.png", dpi=300)
plt.close()