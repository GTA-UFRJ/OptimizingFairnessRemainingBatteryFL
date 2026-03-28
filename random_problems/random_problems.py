from wf_solver import *
import numpy as np
from scipy import stats
import sys

def generate_clients_for_all_executions(num_executions, num_clients, max_time):

    clients_for_each_run = []
    for i in range(num_executions):
        B = np.random.randint(90,110,size=num_clients)
        gamma = 1e-28*np.random.randint(50,55,size=num_clients)
        c = 1e6*np.random.randint(24,36,size=num_clients)
        u = d = 4*8/np.random.randint(40,60,size=num_clients)
        f = 1e8*np.random.randint(28,32,size=num_clients)
        Emax = np.random.randint(1900,2200,size=num_clients) * 10e-3 * 3600 * 3.7
        Eo =  Emax/100 * np.random.randint(10,40,size=num_clients)
        P_down_avg= 0.0000001*Emax

        #max_time = np.random.randint(60,120)
        #min_epochs = num_clients*np.random.randint(8,20)

        clients = [
            Client(Eo[j],B[j],gamma[j],c[j],f[j],P_down_avg[j],0,max_time,u[j],d[j], is_log_active=log) 
            for j in range(num_clients)
            ]
        clients_for_each_run.append(clients)
    return clients_for_each_run

def run_wf(clients_for_each_run, min_epochs, max_time):
    num_executions = len(clients_for_each_run)
    durations = np.zeros(num_executions)
    energies = np.zeros(num_executions)
    final_to_initial_energies = np.zeros(num_executions)
    utilities = np.zeros(num_executions)
    gaps = np.zeros(num_executions)
    times = np.zeros(num_executions)
    energy_stdevs = np.zeros(num_executions)

    for i, clients in enumerate(clients_for_each_run):

        p = WaterFillingSolver(clients, min_epochs, max_time, is_log_active=log, fixed_epochs=fixed_epochs)
        p.solve()

        durations[i] = p.elapsed_time
        energies[i] = p.energy/num_clients
        final_to_initial_energies[i] = 1-p.energy/p.initial_energy
        utilities[i] = p.log_energy
        gaps[i] = p.gap
        times[i] = p.time
        energy_stdevs[i] = p.stdev

    print(f"-----------------------------")
    print(f"Water-Filling")
    print(f"Optimization time = {np.mean(durations)} +- {stats.sem(durations) * stats.t.ppf((1+0.95)/2., len(durations)-1)}s")
    print(f"Round time = {np.mean(times)} +- {stats.sem(times) * stats.t.ppf((1+0.95)/2., len(times)-1)}s")
    print(f"Energy = {np.mean(energies)} +- {stats.sem(energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Energy drop factor = {np.mean(final_to_initial_energies)} +- {stats.sem(final_to_initial_energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Utility = {np.mean(utilities)} +- {stats.sem(utilities) * stats.t.ppf((1+0.95)/2., len(utilities)-1)}s")
    print(f"Gap = {np.mean(gaps)} +- {stats.sem(gaps) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")
    print(f"Energy std. dev. = {np.mean(energy_stdevs)} +- {stats.sem(energy_stdevs) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")

def run_uniform(clients_for_each_run, min_epochs, max_time):
    num_executions = len(clients_for_each_run)
    durations = np.zeros(num_executions)
    energies = np.zeros(num_executions)
    final_to_initial_energies = np.zeros(num_executions)
    utilities = np.zeros(num_executions)
    gaps = np.zeros(num_executions)
    times = np.zeros(num_executions)
    energy_stdevs = np.zeros(num_executions)

    for i, clients in enumerate(clients_for_each_run):

        p = UniformSolver(clients, min_epochs, max_time, is_log_active=log)
        p.solve()

        durations[i] = p.elapsed_time
        energies[i] = p.energy/num_clients
        final_to_initial_energies[i] = 1-p.energy/p.initial_energy
        utilities[i] = p.log_energy
        gaps[i] = p.gap
        times[i] = p.time
        energy_stdevs[i] = p.stdev

    print(f"-----------------------------")
    print(f"Equal number of rounds")
    print(f"Execution time = {np.mean(durations)} +- {stats.sem(durations) * stats.t.ppf((1+0.95)/2., len(durations)-1)}s")
    print(f"Round time = {np.mean(times)} +- {stats.sem(times) * stats.t.ppf((1+0.95)/2., len(times)-1)}s")
    print(f"Energy = {np.mean(energies)} +- {stats.sem(energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Energy drop factor = {np.mean(final_to_initial_energies)} +- {stats.sem(final_to_initial_energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Utility = {np.mean(utilities)} +- {stats.sem(utilities) * stats.t.ppf((1+0.95)/2., len(utilities)-1)}s")
    print(f"Gap = {np.mean(gaps)} +- {stats.sem(gaps) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")
    print(f"Energy std. dev. = {np.mean(energy_stdevs)} +- {stats.sem(energy_stdevs) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")

def run_proportional_energy(clients_for_each_run, min_epochs, max_time):
    num_executions = len(clients_for_each_run)
    durations = np.zeros(num_executions)
    energies = np.zeros(num_executions)
    final_to_initial_energies = np.zeros(num_executions)
    utilities = np.zeros(num_executions)
    gaps = np.zeros(num_executions)
    times = np.zeros(num_executions)
    energy_stdevs = np.zeros(num_executions)

    for i, clients in enumerate(clients_for_each_run):

        p = ProportionalEnergySolver(clients, min_epochs, max_time, is_log_active=log)
        p.solve()

        durations[i] = p.elapsed_time
        energies[i] = p.energy/num_clients
        final_to_initial_energies[i] = 1-p.energy/p.initial_energy
        utilities[i] = p.log_energy
        gaps[i] = p.gap
        times[i] = p.time
        energy_stdevs[i] = p.stdev

    print(f"-----------------------------")
    print(f"Proportional to initial energy")
    print(f"Execution time = {np.mean(durations)} +- {stats.sem(durations) * stats.t.ppf((1+0.95)/2., len(durations)-1)}s")
    print(f"Round time = {np.mean(times)} +- {stats.sem(times) * stats.t.ppf((1+0.95)/2., len(times)-1)}s")
    print(f"Energy = {np.mean(energies)} +- {stats.sem(energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Energy drop factor = {np.mean(final_to_initial_energies)} +- {stats.sem(final_to_initial_energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Utility = {np.mean(utilities)} +- {stats.sem(utilities) * stats.t.ppf((1+0.95)/2., len(utilities)-1)}s")
    print(f"Gap = {np.mean(gaps)} +- {stats.sem(gaps) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")
    print(f"Energy std. dev. = {np.mean(energy_stdevs)} +- {stats.sem(energy_stdevs) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")



def run_proportional_efficiency(clients_for_each_run, min_epochs, max_time):
    num_executions = len(clients_for_each_run)
    durations = np.zeros(num_executions)
    energies = np.zeros(num_executions)
    final_to_initial_energies = np.zeros(num_executions)
    utilities = np.zeros(num_executions)
    gaps = np.zeros(num_executions)
    times = np.zeros(num_executions)
    energy_stdevs = np.zeros(num_executions)

    for i, clients in enumerate(clients_for_each_run):

        p = ProportionalEfficiencySolver(clients, min_epochs, max_time, is_log_active=log)
        p.solve()

        durations[i] = p.elapsed_time
        energies[i] = p.energy/num_clients
        final_to_initial_energies[i] = 1-p.energy/p.initial_energy
        utilities[i] = p.log_energy
        gaps[i] = p.gap
        times[i] = p.time
        energy_stdevs[i] = p.stdev

    print(f"-----------------------------")
    print(f"Proportional to device efficiency")
    print(f"Execution time = {np.mean(durations)} +- {stats.sem(durations) * stats.t.ppf((1+0.95)/2., len(durations)-1)}s")
    print(f"Round time = {np.mean(times)} +- {stats.sem(times) * stats.t.ppf((1+0.95)/2., len(times)-1)}s")
    print(f"Energy = {np.mean(energies)} +- {stats.sem(energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Energy drop factor = {np.mean(final_to_initial_energies)} +- {stats.sem(final_to_initial_energies) * stats.t.ppf((1+0.95)/2., len(energies)-1)}s")
    print(f"Utility = {np.mean(utilities)} +- {stats.sem(utilities) * stats.t.ppf((1+0.95)/2., len(utilities)-1)}s")
    print(f"Gap = {np.mean(gaps)} +- {stats.sem(gaps) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")
    print(f"Energy std. dev. = {np.mean(energy_stdevs)} +- {stats.sem(energy_stdevs) * stats.t.ppf((1+0.95)/2., len(gaps)-1)}s")


if __name__ == "__main__":

    fixed_epochs = 0

    num_clients = int(sys.argv[1]) 
    if len(sys.argv) > 2:
        log = (sys.argv[2] == '1')
    else:
        log = True
    num_executions = 10

    max_time = 25
    min_epochs = num_clients*(9-fixed_epochs)

    clients_for_each_run = generate_clients_for_all_executions(num_executions, num_clients, max_time)

    run_wf(clients_for_each_run.copy(), min_epochs, max_time)

    run_uniform(clients_for_each_run.copy(), min_epochs, max_time)

    run_proportional_energy(clients_for_each_run.copy(), min_epochs, max_time)

    run_proportional_efficiency(clients_for_each_run.copy(), min_epochs, max_time)