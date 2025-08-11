import matplotlib.pyplot as plt
import numpy as np

# Use your custom style
plt.style.use('~/guiaraujo.mplstyle')

solvers = ["WF","Uniform rounds","Prop. energy","Prop. time"]
stdev_soc_8_to_10 = [375,334,0,0]
stdev_soc_8_to_10_err = [92, 3,0,0]


x = np.arange(len(solvers))

fig, ax = plt.subplots(figsize=(12,9))

# 10 to 40
rects = ax.bar(
    x, 
    stdev_soc_8_to_10, 
    yerr=stdev_soc_8_to_10_err,
    width=0.5, 
    label="SoC 8-10%")

ax.set_xticks(x)
ax.set_xticklabels(solvers)
ax.set_xlabel("Method")
ax.set_ylabel("Energy standard deviation")
ax.set_ylim(50,500)

plt.tight_layout()
plt.savefig("plots/stdev_soc_bad_case.png", dpi=300)
plt.close()