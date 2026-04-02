import numpy as np
from matplotlib import pyplot as plt

a = np.array([0,20,40,60,80,100])

energy_drop_factor = np.array([1.7,1.74,1.79,1.85,1.9,2])
energy_drop_factor_error = np.array([0.02,0.01,0.015,0.01,0.01,0.01])

energy_stdev = np.array([4415,4493,4535,4582,4674,4718])
energy_stdev_error = np.array([45,45,43,47,42,40])

plt.style.use('guiaraujo.mplstyle')
plt.rcParams['axes.spines.right'] = True
#f = plt.figure(figsize=(12,9),dpi=300.0)
fig, ax1 = plt.subplots(figsize=(12,9),dpi=300.0)

color = 'tab:red'
ax1.set_xlabel("Percentage of rounds fixed (%)")
ax1.set_ylabel("Energy drop factor (%)",color=color)
#ax1.plot(a, energy_drop_factor, color=color)
ax1.errorbar(a, energy_drop_factor, energy_drop_factor_error, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()

color = 'tab:blue'
ax2.set_ylabel("Energy standard deviation", color=color)
#ax2.plot(a, energy_stdev, color=color)
ax2.errorbar(a, energy_stdev, energy_stdev_error, color=color)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()
fig.savefig("figures/fixed_epochs.png")