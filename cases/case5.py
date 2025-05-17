gamma_i=1e-28
ui=4*8/10 # sending a yolo nano (4MB) in a LTE 10Mbps upload link
di=4*8/15 

clients_parameters = [
    {
        "battery_mAh":2200,
        "starting_soc":0.4,
        "charging_power": 0,
        "batches":100,
        "fi":1e9,
        "ci":0.015 * 1e9
    },
    {
        "battery_mAh":2200,
        "starting_soc":0.5,
        "charging_power": 0,
        "batches":90,
        "fi":1e9,
        "ci":0.015 * 1e9
    },
    {
        "battery_mAh":2200,
        "starting_soc":0.5,
        "charging_power": 0,
        "batches":90,
        "fi":0.9e9,
        "ci":0.011 * 1e9
    }
]

num_min_epochs = 90
time_budget = 60
