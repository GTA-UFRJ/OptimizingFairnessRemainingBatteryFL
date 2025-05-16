from wf_solver import WaterFillingSolver
from client import Client


Bi=100
gamma_i=1e-28
ci=0.015 * 1e9 # sec/batch * cycles/sec = cycles/batch
fi=1e9
ui=4*8/10 # sending a yolo nano (4MB) in a LTE 10Mbps upload link
di=4*8/15 

print("Common parameters:")
print(f"Num batches: {Bi} batches")
print(f"Effective capacitance: {Bi} F")
print(f"Computational efficiency: {Bi} cycles/batch")
print(f"Clock frequency: {fi} Hz")
print(f"Upload time: {ui} s")
print(f"Download time: {di} s")

clients_parameters = [
    {
        "battery_mAh":3000,
        "starting_soc":0.7,
        "charging_power": 1*9*1.5 # 9V 1.5A
    },
    {
        "battery_mAh":3000,
        "starting_soc":0.7,
        "charging_power": 1*5*2 # 5V 2A
    },
    {
        "battery_mAh":3000,
        "starting_soc":0.7,
        "charging_power": 0
    },
    {
        "battery_mAh":2200,
        "starting_soc":0.7,
        "charging_power": 0
    },
    {
        "battery_mAh":2200,
        "starting_soc":0.4,
        "charging_power": 0
    }
]

clients_list = []
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
    clients_list=clients_list[2:],
    num_min_epochs=90,
    time_budget=600,
    thresh=1
)
problem.solve()