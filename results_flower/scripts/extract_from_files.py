import os
import re
import math 
import json
import string
import numpy as np
from pathlib import Path

def extract_val_accuracy(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    except Exception as e:
        print(f"Could not open {filepath}: {e}")
        return []

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
            else:
                capacity = 2050
    return [ capacity*1e-3*3600*3.7*soc/100 for soc in values ]

def extract_epochs_entropy(scenario_dir, run_id, client_indices, num_rounds):
    scenario_dir = Path(scenario_dir)
    client_index_to_num_epochs = {}

    # 1. Extrair os epochs de cada cliente da lista fornecida
    for client_id in client_indices:
        filepath = scenario_dir / f"{run_id}_client{client_id}.logs"
        
        if not filepath.exists():
            continue
            
        with filepath.open("r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        # Regex para capturar os valores antes de "epochs"
        matches = re.findall(r"(\d+\.?\d*)(?=\s+epochs)", text)
        if matches:
            client_index_to_num_epochs[client_id] = [float(x) for x in matches]

    if not client_index_to_num_epochs:
        return [0.0] * num_rounds

    # 2. Agrupar os epochs por rodada (round)
    round_index_to_epochs = {}    
    for round_index in range(num_rounds):
        round_index_to_epochs[round_index] = []
        for client_epochs in client_index_to_num_epochs.values():
            # Verifica se o cliente tem dados para esta rodada específica
            if round_index < len(client_epochs):
                round_index_to_epochs[round_index].append(client_epochs[round_index])
            
    # 3. Calcular a entropia de Shannon para cada rodada
    # H = -sum(p * log2(p))
    round_index_to_entropy = {}
    for round_index, epochs_list in round_index_to_epochs.items():
        total_epochs = sum(epochs_list)
        if total_epochs == 0:
            round_index_to_entropy[round_index] = 0.0
            continue
            
        entropy = 0
        for epochs in epochs_list:
            p = epochs / total_epochs 
            if p > 0:
                entropy -= p * math.log2(p)
        
        round_index_to_entropy[round_index] = entropy

    # 4. Normalização
    # O valor máximo de entropia é log2(N), onde N é o número de clientes
    n_clients = len(client_index_to_num_epochs)
    max_entropy = math.log2(n_clients) if n_clients > 1 else 1.0
    
    normalized_entropies = [
        round_index_to_entropy[r] / max_entropy 
        for r in range(num_rounds)
    ]

    return normalized_entropies

def analyse_run(scenario_dir, run_id, client_indices):
    scenario_dir = Path(scenario_dir)
    server_log = scenario_dir / f"{run_id}_server.logs"
    
    # 1. Extração de acurácia do servidor
    # (Mantendo str() caso a função original não suporte Path)
    acc = extract_val_accuracy(str(server_log))
    num_rounds = len(acc)
    
    if num_rounds == 0:
        print(f"Consequence: could not analyse run {run_id} of scenario {scenario_dir}")
        return None
    
    final_acc = acc[-1]

    # 2. Extração de entropia
    # Nota: Certifique-se de que a extract_epochs_entropy também aceite a lista client_indices
    entropies = extract_epochs_entropy(scenario_dir, run_id, client_indices, num_rounds)

    # 3. Evolução de energia por cliente (usando a lista de índices)
    client_to_energy_evolution_map = {}
    for client_id in client_indices:
        client_to_energy_evolution_map[f"client_{client_id}"] = extract_energies(scenario_dir, run_id, client_id)

    # 4. Cálculo de Fairness baseado na energia final
    # Filtramos apenas clientes que terminaram com energia positiva
    final_energies = [
        v[-1] for v in client_to_energy_evolution_map.values() 
        if len(v) > 0 and v[-1] > 0
    ]

    # No seu código original, log_energy era calculado e depois sobrescrito pelo np.std.
    # Segui com o desvio padrão (std) conforme a última atribuição do seu snippet.
    fairness_val = np.std(final_energies) if final_energies else 0

    return {
        "acc_history": acc, 
        "entropy_history": entropies, 
        "accuracy": final_acc, 
        "energy_history": client_to_energy_evolution_map, 
        "fairness": fairness_val
    }

def analyse_scenario(scenario_dir):
    scenario_dir = Path(scenario_dir)
    
    # Dicionário para mapear { server_index: [client_index1, client_index2, ...] }
    server_structure = {}

    # 1. Identificar todos os servidores disponíveis
    server_files = scenario_dir.rglob('*_server.logs')
    for f in server_files:
        # Extrai o número que vem antes de '_server'
        match = re.search(r'(\d+)_server', f.name)
        if match:
            server_id = int(match.group(1))
            if server_id not in server_structure:
                server_structure[server_id] = []

    # 2. Identificar os clientes e associá-los aos seus respectivos servidores
    client_files = scenario_dir.rglob('*_client*.logs')
    for f in client_files:
        # Extrai o ID do servidor (X) e o ID do cliente (Y) de 'X_clientY.logs'
        match = re.search(r'(\d+)_client(\d+)', f.name)
        if match:
            s_id = int(match.group(1))
            c_id = int(match.group(2))
            
            # Só adiciona se o servidor correspondente existir
            if s_id in server_structure:
                server_structure[s_id].append(c_id)

    # Ordenar os índices para garantir consistência no processamento
    for s_id in server_structure:
        server_structure[s_id].sort()

    # 3. Chamar a analyse_run passando a lista de índices de clientes
    # Note que agora passamos 'client_indices' em vez de 'num_clients'
    repetition_to_result_map = {
        run_id: analyse_run(scenario_dir, run_id, client_indices) 
        for run_id, client_indices in server_structure.items()
    }
    
    return {k: v for k, v in repetition_to_result_map.items() if v is not None}

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

    #print_dict_struct(scenarios_to_results_map, save=os.path.join(my_dir,"results/results_struct"))

    with open(os.path.join(my_dir,"processed/results.json"),"w") as f:
        json.dump(scenarios_to_results_map,f, indent=4)