from math import floor, ceil
from numpy import math
from time import time
from scipy import stats

def _print(text):
    global log
    if log:
        print(text)

class WaterFillingSolver:
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        thresh:int=1,
        is_log_active=True,
        fixed_epochs:int=0):
        
        self.clients_list = clients_list
        self.num_clients = len(clients_list)
        self.time_budget = time_budget        
        self.e = thresh

        global log
        log = is_log_active

        self._run_fixed_num_epochs(fixed_epochs)

        self.csi = self._compute_ceil_num_epochs()
        _print(f"Suppose clients will train for {self.csi} epochs. Lets reduce that!")
        self.R = self.num_clients * self.csi  - num_min_epochs

        self._compute_Nis()
        #self.U = (self.R + sum(self.Ni_list)) / self.num_clients
        self.U = self.R + max(self.Ni_list)
        self.L = min(self.Ni_list) #-self.U

    def _run_fixed_num_epochs(self, fixed_epochs):
        for client in self.clients_list:
            client.Ti = client.tau_i * fixed_epochs
            client.Eio = client.Eio - (client.P_down_avg-client.Pi)*client.Ti - fixed_epochs*client.epsilon_i

    def _compute_Nis(self):
        # Interpretation for Ni:
        # Suppose the client trained for the maximum number of epochs (ri = 0)
        # What is the number of epochs the client must train do drain its
        # remaining energy to zero?
        self.Ni_list = [client._compute_Ni(self.csi) for client in self.clients_list]
            
    def _compute_ceil_num_epochs(self):
        return max([floor((self.time_budget-client.ui-client.di)/client.tau_i) for client in self.clients_list])

    def _update_clients(self):
        self.new_clients_list = []

        # DEBUG !!!
        #self.r_list = [11.22444691113742, 36, 0]
        
        for client, r in zip(self.clients_list, self.r_list):
            client.compute(r, self.csi) 
            self.new_clients_list.append(client)
        self.clients_list = self.new_clients_list

    def _run_iteration(self):
        alfa = (self.U + self.L)/2
        self.r_list = []
        for i, Ni in enumerate(self.Ni_list):
            # If there is a positive Ni, do not reduce num of epochs for negative Nis
            #if self.clients_list[i].Ki < 0 and len([Ni for Ni in self.Ni_list if Ni>=0]) > 0:
            #    ri = 0
            #else:
            #    ri = alfa - Ni
            ri = alfa - Ni
            if ri > 0 and ri <= self.csi:
                self.r_list.append(ri)
            elif ri > 0  and ri > self.csi:
                self.r_list.append(self.csi)
            else:
                self.r_list.append(0)

        _print(f"U = {self.U}")
        _print(f"L = {self.L}")
        _print(f"alpha = {alfa}")
        _print(f"Nis = {self.Ni_list}")
        _print(f"rs = {self.r_list}")
        self._update_clients()
        self.t_list = [client.Ti for client in self.clients_list]
        if sum(self.r_list) > self.R: #or self.time_budget > max(self.t_list):
            self.U = alfa
            _print("Decrease U!")
        else:
            self.L = alfa
            _print("Increase L!")


    def _bootstraping_for_time_constrain(self):
        # max num of rounds each client can train without surpassing time budget
        ns = [floor((self.time_budget-client.ui-client.di)/client.tau_i) for client in self.clients_list]
        self.r_list = [ceil(self.csi - n) for n in ns]
        _print(f"Starting r values: {self.r_list}") 
        self._update_clients()
        return

    def solve(self):
        start_time = time()
        self._bootstraping_for_time_constrain()
        i = 1
        _print(f"--------- ITERATION {i} ---------")
        _print(f"R = {self.R}")
        self._run_iteration() 
        while abs(self.R - sum(self.r_list)) > self.e: # and (self.U - self.L) > 1:
            i += 1
            if i >= 100:
                break
            _print(f"--------- ITERATION {i} ---------")
            self._run_iteration()
        self.elapsed_time = time()-start_time
        self._report()

    def _report(self,force_print=False):
        global log
        old_log = log
        if force_print:
            log=True
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
            self.initial_energy += client.original_Eio
            if client.Ti > self.time:
                self.time = client.Ti
        _print(f"TOTAL ENERGY: {self.energy}")
        _print(f"INITIAL ENERGY: {self.initial_energy}")
        _print(f"TOTAL FAIRNESS: {self.log_energy}")
        
        top = max([client.original_Eio for client in self.clients_list])
        self.gap = sum([1 - client.Ei/top for client in self.clients_list])/self.num_clients
        _print(f"ENERGY GAP TO MAX: {self.gap}")

        E_list = [client.Ei for client in self.clients_list]
        self.E_list = E_list
        self.stdev = stats.sem(E_list) * stats.t.ppf((1+0.95)/2., len(E_list)-1)
        _print(f"ENERGY STANDARD DEVIATION: {self.stdev}")

        _print(f"ELAPSED TIME: {self.elapsed_time}")
        log = old_log
