import os
import re
import math 
import json
import string

def print_dict_struct(d):        
    def print_tabs(n):
        for _ in range(n): 
            print('  ',end='')
    def print_nested_dict_keys(d:dict,n=0):
        print_tabs(n)
        print('{')
        for key, value in d.items():
            n+=1
            print_tabs(n)
            print(key)
            if isinstance(value, dict):
                print_nested_dict_keys(value,n)
            n-=1
        print_tabs(n)
        print('}')
    import sys
    s = sys.stdout
    sys.stdout = open(os.path.join(my_dir,"results_struct"),'w')
    print_nested_dict_keys(d)
    sys.stdout = s

def extract_val_accuracy(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    text = re.sub(r"\x1b\[[0-9;]*m", "", text)   # limpa códigos de cor ANSI
    text = re.sub(r"INFO\s*:\s*", "", text)      # remove prefixos INFO:

    # Agora procura o trecho 'val_accuracy': [...]
    match = re.search(r"'val_accuracy':\s*(\[[^\]]*\])", text, re.DOTALL)
    if not match:
        print("Accuracy not found")
        return []

    # Converte string para lista de tuplas Python
    val_accuracy_list = eval(match.group(1))

    # Pega só as acurácias (segundo elemento da tupla)
    accuracies = [acc for _, acc in val_accuracy_list]
    return accuracies

def extract_energies(filepath):
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

def analyse_run(run_dir):
    acc = extract_val_accuracy(os.path.join(run_dir,"server.logs"))
    if len(acc) == 0:
        return None
    final_acc = acc[-1]

    client_to_energy_evolution_map = {}
    for i in range(10):
        client_to_energy_evolution_map[f"client_{i}"] = extract_energies(os.path.join(run_dir, f"client{i}.logs"))

    client_to_energy_map = { k:v[-1] for k,v in client_to_energy_evolution_map.items() }

    log_energy = sum([ math.log10(final_energy) for final_energy in client_to_energy_map.values() ])

    return {
        "acc_history": acc, # TODO: plot example of convergence
        "accuracy": final_acc, 
        "energy_history":  client_to_energy_evolution_map, # TODO: plot example of batteries consumption
        "fairness": log_energy
    }

def analyse_scenario(scenario_dir):
    reptition_to_result_map = { repetition_dir : analyse_run(os.path.join(scenario_dir,repetition_dir)) 
                                for repetition_dir in os.listdir(scenario_dir) }
    return {k:v for k,v in reptition_to_result_map.items() if k is not None}
        

if __name__ == "__main__":
    my_dir = os.path.dirname(__file__)
    print(my_dir)
    results_dir = os.path.join(my_dir,"../flower")

    scenarios_to_results_map = {
        "fixed_0_variable_50_lr_001":{},
        "fixed_25_variable_25_lr_001":{},
        "fixed_50_variable_0_lr_001":{}
    }

    scenarios_list = scenarios_to_results_map.keys()
    for scenario in scenarios_list:
        scenarios_to_results_map[scenario] = analyse_scenario(os.path.join(results_dir,scenario))

    print_dict_struct(scenarios_to_results_map)

    with open(os.path.join(my_dir,"results.json"),"w") as f:
        json.dump(scenarios_to_results_map,f, indent=4)