import argparse
import json
import sys
from wf_solver import *

def main():
    parser = argparse.ArgumentParser(description="Executa o WaterFillingSolver com base em um arquivo JSON.")
    parser.add_argument("config_file", help="Caminho para o arquivo de configuração JSON (ex: case4.json)")
    args = parser.parse_args()

    try:
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{args.config_file}' não foi encontrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{args.config_file}' não é um JSON válido.")
        sys.exit(1)

    defaults = {
        "num_min_epochs": 60,
        "time_budget": 60,
        "gamma_i": 1e-28,
        "ui": 4 * 8 / 10,  # 3.2 s
        "di": 4 * 8 / 15,  # ~2.13 s
        "batches": 100,    # Equivalente ao Bi
        "ci": 0.015 * 1e9,
        "fi": 1e9,
        "battery_mAh": 3000,
        "starting_soc": 0.7,
        "charging_power": 0
    }

    global_params = config.get("global_parameters", {})
    for key, value in global_params.items():
        defaults[key] = value

    clients_config = config.get("clients", [])
    if not clients_config:
        print("Erro: Nenhum cliente ('clients') foi definido no arquivo JSON.")
        sys.exit(1)

    print("--- Parâmetros Globais ---")
    print(f"Épocas mínimas: {defaults['num_min_epochs']}")
    print(f"Time budget: {defaults['time_budget']} s")
    print(f"Capacitância efetiva (gamma_i): {defaults['gamma_i']} F")
    print(f"Tempo de Upload (ui): {defaults['ui']} s")
    print(f"Tempo de Download (di): {defaults['di']} s\n")
    
    clients_list = []
    
    for i, c_conf in enumerate(clients_config):
        print(f"--- Cliente {i+1} ---")
        
        Bi = c_conf.get("batches", defaults["batches"])
        ci = c_conf.get("ci", defaults["ci"])
        fi = c_conf.get("fi", defaults["fi"])
        battery_mAh = c_conf.get("battery_mAh", defaults["battery_mAh"])
        starting_soc = c_conf.get("starting_soc", defaults["starting_soc"])
        charging_power = c_conf.get("charging_power", defaults["charging_power"])
        
        Emax = battery_mAh * 10e-3 * 3600 * 3.7 
        Eio = starting_soc * Emax
        P_down_avg = 0.00000023 * Emax
        Pi = charging_power

        print(f"Num batches (Bi): {Bi}")
        print(f"Eficiência computacional (ci): {ci} ciclos/batch")
        print(f"Clock frequency (fi): {fi} Hz")
        print(f"Eio inicial: {Eio:.2f} J")
        print(f"Potência de carregamento (Pi): {Pi} J\n")

        client = Client(
            Eio=Eio, 
            Bi=Bi, 
            gamma_i=defaults["gamma_i"], 
            ci=ci, 
            fi=fi, 
            P_down_avg=P_down_avg, 
            Pi=Pi, 
            max_time=defaults["time_budget"], 
            ui=defaults["ui"], 
            di=defaults["di"]
        )
        clients_list.append(client)

    problem = WaterFillingSolver(
        clients_list=clients_list.copy(),
        num_min_epochs=defaults["num_min_epochs"],
        time_budget=defaults["time_budget"]
    )
    problem.solve()

    problem = UniformSolver(
        clients_list=clients_list.copy(),
        num_min_epochs=defaults["num_min_epochs"],
        time_budget=defaults["time_budget"]
    )
    problem.solve()

    problem = ProportionalEnergySolver(
        clients_list=clients_list.copy(),
        num_min_epochs=defaults["num_min_epochs"],
        time_budget=defaults["time_budget"]
    )
    problem.solve()

    problem = ProportionalEfficiencySolver(
        clients_list=clients_list.copy(),
        num_min_epochs=defaults["num_min_epochs"],
        time_budget=defaults["time_budget"]
    )
    problem.solve()

if __name__ == "__main__":
    main()