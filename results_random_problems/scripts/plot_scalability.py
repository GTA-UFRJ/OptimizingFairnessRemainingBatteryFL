import numpy as np
from matplotlib import pyplot as plt

'''
0.000349581241607666 +- 1.2817716157648559e-05s
0.0033124613761901854 +- 9.62231709406005e-05s
0.04533381938934326 +- 0.0007763176070095852s
0.6155314064025879 +- 0.00871800746924831s
'''

a = np.array([10,100,1000,10000])
WF = np.array([0.000349581241607666, 0.0033124613761901854, 0.04533381938934326, 0.6155314064025879])
WF_error = np.array([1.2817716157648559e-05, 9.62231709406005e-05, 0.0007763176070095852, 0.00871800746924831])

plt.style.use('guiaraujo.mplstyle')
f = plt.figure(figsize=(12,9),dpi=300.0)

lines = [None]
lines[0], = plt.plot(a, WF, label="WF",color="red")
plt.errorbar(a, WF, WF_error, color="red")

plt.xlabel("Num. of clients")
plt.ylabel("Execution time (s)")
plt.xscale('log')
plt.yscale('log')
plt.ylim([10e-5,10])
plt.legend(handles=lines)
#plt.show()
f.savefig("figures/scalability.png")