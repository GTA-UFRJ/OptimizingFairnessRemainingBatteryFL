from wf_solver import WaterFillingSolver
from client import Client
from cases.case2 import *

print("Common parameters:")
print(f"Num batches: {Bi} batches")
print(f"Effective capacitance: {gamma_i} F")
print(f"Computational efficiency: {ci} cycles/batch")
print(f"Clock frequency: {fi} Hz")
print(f"Upload time: {ui} s")
print(f"Download time: {di} s")

clients_list = []
print(clients_parameters)
for i, client_parameters in enumerate(clients_parameters):
    print(f"Client {i+1}")
    Emax = client_parameters["battery_mAh"] * 10e-3 * 3600 * 3.7 # mAh * 10e-3 A/mA * 3600 s/h * V = VAs = Ws = J
    Eio = client_parameters["starting_soc"] * Emax
    P_down_avg= 0.00000023*Emax
    Pi = client_parameters["charging_power"]
    print(f"Eio: {Eio} J")
    print(f"Pi: {Pi} J")
    client = Client(Eio, Bi, gamma_i, ci, fi, P_down_avg, Pi, ui, di)
    clients_list.append(client)

problem = WaterFillingSolver(
    clients_list=clients_list,
    num_min_epochs=num_min_epochs,
    time_budget=time_budget
)
problem.solve()