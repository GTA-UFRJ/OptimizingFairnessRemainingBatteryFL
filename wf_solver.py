from math import floor, ceil
from numpy import math

class WaterFillingSolver:
    def __init__(
        self,
        clients_list:list,
        num_min_epochs:int,
        time_budget:float,
        thresh:int=1) -> None:
        
        self.clients_list = clients_list
        self.num_clients = len(clients_list)
        self.time_budget = time_budget        
        self.e = thresh

        self.csi = self._compute_ceil_num_epochs()
        print(f"Suppose clients will train for {self.csi} epochs. Lets reduce that!")
        self.R = self.num_clients * self.csi  - num_min_epochs

        self._compute_Nis()
        #self.U = (self.R + sum(self.Ni_list)) / self.num_clients
        self.U = self.R + max(self.Ni_list)
        self.L = min(self.Ni_list) #-self.U

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

        print(f"U = {self.U}")
        print(f"L = {self.L}")
        print(f"alpha = {alfa}")
        print(f"Nis = {self.Ni_list}")
        print(f"rs = {self.r_list}")
        self._update_clients()
        self.t_list = [client.Ti for client in self.clients_list]
        if sum(self.r_list) > self.R: #or self.time_budget > max(self.t_list):
            self.U = alfa
            print("Decrease U!")
        else:
            self.L = alfa
            print("Increase L!")


    def _bootstraping_for_time_constrain(self):
        # max num of rounds each client can train without surpassing time budget
        ns = [floor((self.time_budget-client.ui-client.di)/client.tau_i) for client in self.clients_list]
        self.r_list = [ceil(self.csi - n) for n in ns]
        print(f"Starting r values: {self.r_list}") 
        self._update_clients()
        return

    def solve(self):
        self._bootstraping_for_time_constrain()
        i = 1
        print(f"--------- ITERATION {i} ---------")
        print(f"R = {self.R}")
        self._run_iteration() 
        while abs(self.R - sum(self.r_list)) > self.e: # and (self.U - self.L) > 1:
            i += 1
            if i >= 100:
                break
            print(f"--------- ITERATION {i} ---------")
            self._run_iteration()
        self._report()

    def _report(self):
        log_energy = 0
        for i, client in enumerate(self.clients_list):
            print(f"---------------")
            print(f"Client {i+1}")
            client.report()
            log_energy += math.log10(client.Ei)
        print(f"TOTAL FAIRNESS: {1/log_energy}")
        