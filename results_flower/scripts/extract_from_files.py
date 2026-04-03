import os
import re
import math 
import json
import string
import numpy as np
from utils import print_dict_struct

def extract_val_accuracy(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    text = re.sub(r"\x1b\[[0-9;]*m", "", text)   # limpa códigos de cor ANSI
    text = re.sub(r"INFO\s*:\s*", "", text)      # remove prefixos INFO:
    
    # Agora procura o trecho 'val_accuracy': [...]
    match = re.search(r"'val_accuracy':\s*(\[[^\]]*\])", text, re.DOTALL)

    if not match:
        print("Accuracy not found in ", filepath)
        return []
    else:
        print("Accuracy found in ", filepath)

    # Converte string para lista de tuplas Python
    val_accuracy_list = eval(match.group(1))

    # Pega só as acurácias (segundo elemento da tupla)
    accuracies = [acc for _, acc in val_accuracy_list]
    return accuracies

def extract_energies(scenario_dir, run_id, client_id):
    filepath = os.path.join(scenario_dir, f"{run_id}_client{client_id}.logs")
    values = []
    capacity = None
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for l in f:
            line = ''.join([x for x in l if x in string.printable])
            match = re.search(r"New battery SoC:\s*([0-9.+-eE]+)", line)
            if match:
                values.append(float(match.group(1)))

            match = re.search(r'"battery_mAh":\s*([0-9]+)', line)
            if match:
                capacity = int(match.group(1))  # guarda o último valor encontrado
    return [ capacity*1e-3*3600*3.7*soc/100 for soc in values ]

def extract_epochs_entropy(scenario_dir, run_id, num_clients, num_rounds):
    client_index_to_num_epochs = {}
    for client_id in range(num_clients):
        filepath = os.path.join(scenario_dir, f"{run_id}_client{client_id}.logs")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        # search for lines in the format Received report: {'num_epochs': 5.0} and transform to list of num_epochs
        matches = re.findall(r"(\d+\.?\d*)(?=\s+epochs)", text)
        if matches:
            client_index_to_num_epochs[client_id] = [float(x) for x in matches]

    round_index_to_epochs = {}    
    for round_index in range(num_rounds):
        for client_epochs in client_index_to_num_epochs.values():
            epochs = client_epochs[round_index]
            if round_index not in round_index_to_epochs:
                round_index_to_epochs[round_index] = []
            round_index_to_epochs[round_index].append(epochs)
            
    # For each round, compute entropy of epochs distribution
    round_index_to_entropy = {}
    for round_index, epochs_list in round_index_to_epochs.items():
        total_epochs = sum(epochs_list)
        entropy = 0
        for epochs in epochs_list:
            p = epochs / total_epochs 
            if p > 0:
                entropy += -p * math.log2(p)
            else:
                entropy += 0
        round_index_to_entropy[round_index] = entropy

    # generate a list of NORMALIZED entropies
    max_entropy = math.log2(len(client_index_to_num_epochs))  # maximum entropy possible
    normalized_entropies = [ round_index_to_entropy[round_index]/max_entropy for round_index in sorted(round_index_to_entropy.keys()) ]

    return normalized_entropies 

def analyse_run(scenario_dir, run_id, num_clients):
    acc = extract_val_accuracy(os.path.join(scenario_dir,f"{run_id}_server.logs"))
    num_rounds = len(acc)
    if len(acc) == 0:
        return None
    final_acc = acc[-1]

    entropies = extract_epochs_entropy(scenario_dir, run_id, num_clients, num_rounds)

    client_to_energy_evolution_map = {}
    for client_id in range(num_clients):
        client_to_energy_evolution_map[f"client_{client_id}"] = extract_energies(scenario_dir, run_id, client_id)

    #print(client_to_energy_evolution_map)

    client_to_energy_map = {}
    for k,v in client_to_energy_evolution_map.items():
        if v[-1] > 0:
            client_to_energy_map[k] = v[-1]

    log_energy = sum([ math.log10(final_energy) for final_energy in client_to_energy_map.values() ])

    log_energy = np.std([ final_energy for final_energy in client_to_energy_map.values() ])

    return {
        "acc_history": acc, # TODO: plot example of convergence
        "entropy_history": entropies, # TODO: plot example of selection entropy
        "accuracy": final_acc, 
        "energy_history":  client_to_energy_evolution_map, # TODO: plot example of batteries consumption
        "fairness": log_energy
    }

def analyse_scenario(scenario_dir):
    num_servers = len([f for f in scenario_dir.rglob('*server*')   if f.is_file()])
    num_clients = len([f for f in scenario_dir.rglob('*1_client*')   if f.is_file()])

    reptition_to_result_map = { run_id : analyse_run(scenario_dir, run_id, num_clients) 
                                for run_id in range(num_servers) }
    
    return {k:v for k,v in reptition_to_result_map.items() if k is not None}
        

if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    results_dir = os.path.join(my_dir,"logs/")

    scenarios_to_results_map = {
        "fixed_0_variable_50":{},
        #"fixed_25_variable_25":{},
        "fixed_50_variable_0":{}
    }

    scenarios_list = scenarios_to_results_map.keys()
    for scenario in scenarios_list:
        scenarios_to_results_map[scenario] = analyse_scenario(os.path.join(results_dir,scenario))

    print_dict_struct(scenarios_to_results_map, save=os.path.join(my_dir,"results/results_struct"))

    with open(os.path.join(my_dir,"processed/results.json"),"w") as f:
        json.dump(scenarios_to_results_map,f, indent=4)