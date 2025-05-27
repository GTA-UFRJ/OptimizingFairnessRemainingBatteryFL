from wf_solver import WaterFillingSolver
from client import Client
import numpy as np
from scipy import stats
import sys

num_clients = int(sys.argv[1]) 
num_executions = 100

durations = np.zeros(num_executions)
energies = np.zeros(num_executions)
utilities = np.zeros(num_executions)
gaps = np.zeros(num_executions)

for i in range(num_executions):
    B = np.random.randint(90,110,size=num_clients)
    gamma = 1e-29*np.random.randint(24,28,size=num_clients)
    c = 1e6*np.random.randint(24,36,size=num_clients)
    u = d = 4*8/np.random.randint(40,60,size=num_clients)
    f = 1e8*np.random.randint(28,32,size=num_clients)
    Emax = np.random.randint(1900,2300,size=num_clients) * 10e-3 * 3600 * 3.7
    Eo =  Emax/100 * np.random.randint(10,20,size=num_clients)
    P_down_avg= 0.0000001*Emax

    max_time = np.random.randint(60,120)
    min_epochs = num_clients*np.random.randint(8,20)
    
    clients = [Client(Eo[j],B[j],gamma[j],c[j],f[j],P_down_avg[j],0,max_time,u[j],d[j]) for j in range(num_clients)]
    p = WaterFillingSolver(clients, min_epochs, max_time)
    p.solve()

    durations[i] = p.elapsed_time
    energies[i] = p.energy/num_clients
    utilities[i] = p.log_energy
    gaps[i] = p.gap

print(f"-----------------------------")
print(f"Time = {np.mean(durations)} +- {stats.sem(durations) * stats.t.ppf((1+0.95)/2., len(durations)-1)}s")
print(f"Energy = {np.mean(energies)} +- {stats.sem(energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
print(f"Utility = {np.mean(utilities)} +- {stats.sem(utilities) * stats.t.ppf((1+0.95)/2., len(utilities)-1)}s")
print(f"Gap = {np.mean(gaps)} +- {stats.sem(gaps) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")