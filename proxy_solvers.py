from math import floor, ceil
from numpy import math
from time import time
from scipy import stats

def _print(text):
    global log
    if log:
        print(text)

class Solver:
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        is_log_active=True) -> None:

        self.clients_list = clients_list
        self.num_clients = len(clients_list)
        self.time_budget = time_budget        

        global log
        log = is_log_active

        self.csi = max([floor((self.time_budget-client.ui-client.di)/client.tau_i) for client in self.clients_list])
        self.R = self.num_clients * self.csi  - num_min_epochs
    
    def _report(self):
        self.log_energy = 0
        self.energy = 0
        self.initial_energy = 0
        self.time = 0
        for i, client in enumerate(self.clients_list):
            _print(f"---------------")
            _print(f"Client {i+1}")
            client.report()
            self.log_energy += math.log10(client.Ei)
            self.energy += client.Ei
            self.initial_energy += client.Eio
            if client.Ti > self.time:
                self.time = client.Ti
        _print(f"TOTAL ENERGY: {self.energy}")
        _print(f"INITIAL ENERGY: {self.initial_energy}")
        _print(f"TOTAL FAIRNESS: {self.log_energy}")
        
        top = max([client.Ei for client in self.clients_list])
        self.gap = sum([1 - client.Ei/top for client in self.clients_list])/self.num_clients
        _print(f"ENERGY GAP TO MAX: {self.gap}")

        E_list = [client.Ei for client in self.clients_list]
        self.E_list = E_list
        self.stdev = stats.sem(E_list) * stats.t.ppf((1+0.95)/2., len(E_list)-1)
        _print(f"ENERGY STANDARD DEVIATION: {self.stdev}")

        _print(f"ELAPSED TIME: {self.elapsed_time}")

class UniformSolver(Solver):
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        is_log_active=True) -> None:
        
        super().__init__(clients_list,num_min_epochs,time_budget,is_log_active)

    def solve(self):
        start_time = time()

        ri = self.R/len(self.clients_list)
        self.new_clients_list = []

        for client in self.clients_list:
            client.compute(ri, self.csi)
            self.new_clients_list.append(client)

        self.clients_list = self.new_clients_list

        self.elapsed_time = time()-start_time

        self._report()

class ProportionalEnergySolver(Solver):
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        is_log_active=True) -> None:
        
        super().__init__(clients_list,num_min_epochs,time_budget,is_log_active)

    def solve(self):
        start_time = time()

        total_energy = 0
        for client in self.clients_list:
            total_energy += client.Eio 

        r_list = []
        for client in self.clients_list:
            r_list.append(self.R * client.Eio/total_energy)
        
        self.new_clients_list = []
        for i, client in enumerate(self.clients_list):
            client.compute(r_list[i], self.csi)
            self.new_clients_list.append(client)

        self.clients_list = self.new_clients_list

        self.elapsed_time = time()-start_time

        self._report()

class ProportionalEfficiencySolver(Solver):
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        is_log_active=True) -> None:
        
        super().__init__(clients_list,num_min_epochs,time_budget,is_log_active)

    def solve(self):
        start_time = time()

        total_inverse_round_power = 0
        for c in self.clients_list:
            round_consumption = c.P_down_avg - c.Pi + c.epsilon_i/c.tau_i 
            total_inverse_round_power +=  1/round_consumption

        r_list = []
        for c in self.clients_list:
            round_consumption = c.P_down_avg - c.Pi + c.epsilon_i/c.tau_i 
            r_list.append(self.R * (1/round_consumption) / total_inverse_round_power)
        
        self.new_clients_list = []
        for i, client in enumerate(self.clients_list):
            client.compute(r_list[i], self.csi)
            self.new_clients_list.append(client)

        self.clients_list = self.new_clients_list

        self.elapsed_time = time()-start_time

        self._report()