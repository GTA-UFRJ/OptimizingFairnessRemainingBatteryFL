Bi=100
gamma_i=1e-28
ci=0.015 * 1e9 # sec/batch * cycles/sec = cycles/batch
fi=1e9
ui=4*8/10 # sending a yolo nano (4MB) in a LTE 10Mbps upload link
di=4*8/15 

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
        "battery_mAh":3100,
        "starting_soc":0.7,
        "charging_power": 1*9*1.5 
    }
]

num_min_epochs = 60
time_budget = 60
