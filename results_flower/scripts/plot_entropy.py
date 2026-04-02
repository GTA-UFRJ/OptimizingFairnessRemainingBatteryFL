import pickle
import os
from matplotlib import pyplot as plt
from matplotlib import patches 
from utils import print_dict_struct
from pprint import pprint

def plot_entropy(scenario_params:dict, save_path:str):
    plt.style.use('guiaraujo.mplstyle')
    plt.figure(figsize=(12,9))

    for scenario, params in scenario_params.items():
        sequence = params["sequence"]
        error = params["error"]
        name = params["name"]
        color = params["color"]

        rounds = [ x[0] for x in sequence ]
        entropies = [ x[1] for x in sequence ]

        plt.errorbar(rounds, entropies, yerr=error, label=name, color=color, capsize=3)

    plt.xlabel("Rodada")
    plt.ylabel("Entropia Normalizada")
    #plt.title("Evolução da Entropia de Seleção ao Longo das Rodadas")
    plt.ylim(0,1.2)
    plt.legend()
    plt.savefig(save_path)
    plt.close()


if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    
    with open(os.path.join(my_dir,"results.pkl"),'rb') as f:
        d = pickle.load(f)

    scenario_params = {
        "fixed_100_variable_0_lr_001": {
            "name": "k=1 (100 épocas fixas)",
            "color": "red",
            "sequence": None,
            "error": None
        },
        "fixed_50_variable_50_lr_001": {
            "name": "k=0,5 (50 épocas fixas)",
            "color": "green",
            "sequence": None,
            "error": None
        },
        "fixed_0_variable_100_lr_001": {
            "name": "k=0 (0 épocas fixas)",
            "color": "blue",
            "sequence": None,
            "error": None
        },
    }


    for scenario, info in d.items():
        scenario_params[scenario]["sequence"] = [
            (round_index, avg_entropy) 
            for round_index, (avg_entropy, err) in info["entropy_history"].items()
        ]
        scenario_params[scenario]["error"] = [
            err 
            for round_index, (avg_entropy, err) in info["entropy_history"].items()
        ]

    # Call a function that plots one line with error bars for each scenario
    plot_entropy(scenario_params, save_path=os.path.join(my_dir,"entropy_plot.png"))