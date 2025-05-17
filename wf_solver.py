from client import Client
from math import floor

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
        self.U = (self.R + sum(self.Ni_list)) / self.num_clients
        self.U = self.R + max(self.Ni_list)
        self.L = 0 #-self.U

    def _compute_Nis(self):
        self.Ni_list = [(client.Eio - self.csi * client.Ki) / client.Ki for client in self.clients_list]
            
    def _compute_ceil_num_epochs(self):
        return max([floor(self.time_budget/client.tau_i) -client.ui-client.di for client in self.clients_list])

    def _update_clients(self):
        self.new_clients_list = []
        for client, r in zip(self.clients_list, self.r_list):
            client.compute(r, self.csi) 
            self.new_clients_list.append(client)
        self.clients_list = self.new_clients_list

    def _run_iteration(self):
        alfa = (self.U + self.L)/2
        self.r_list = []
        for Ni in self.Ni_list:
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


    def solve(self):
        i = 1
        print(f"--------- ITERATION {i} ---------")
        self._run_iteration() 
        while abs(self.R - sum(self.r_list)) > self.e: # and (self.U - self.L) > 1:
            i += 1
            if i >= 100:
                break
            print(f"--------- ITERATION {i} ---------")
            print(f"R = {self.R}")
            self._run_iteration()
        self._report()

    def _report(self):
        for i, client in enumerate(self.clients_list):
            print(f"---------------")
            print(f"Client {i+1}")
            client.report()
        