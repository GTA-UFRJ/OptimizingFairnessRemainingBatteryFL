from typing import List, Tuple
from pathlib import Path
from flwr.common import Metrics, ndarrays_to_parameters
from flwr.server import ServerConfig, start_server
from flwr.server.strategy import FedAvg
import json
from wf_solver import *
import sys
import subprocess
import time

from task import MLP, get_weights

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    examples = [num_examples for num_examples, _ in metrics]

    train_losses = [num_examples * m["train_loss"] for num_examples, m in metrics]
    train_accuracies = [
        num_examples * m["train_accuracy"] for num_examples, m in metrics
    ]
    val_losses = [num_examples * m["val_loss"] for num_examples, m in metrics]
    val_accuracies = [num_examples * m["val_accuracy"] for num_examples, m in metrics]

    acc = sum(val_accuracies) / sum(examples)
    print(acc)

    return {
        "train_loss": sum(train_losses) / sum(examples),
        "train_accuracy": sum(train_accuracies) / sum(examples),
        "val_loss": sum(val_losses) / sum(examples),
        "val_accuracy": sum(val_accuracies) / sum(examples),
    }

class ModFedAvg(FedAvg):
    def __init__(
        self, net, num_min_epochs, time_budget, fixed_epochs, num_clients
    ) -> None:
        self.num_clients = num_clients
        ndarrays = get_weights(net)
        parameters = ndarrays_to_parameters(ndarrays)
        self.num_min_epochs = num_min_epochs
        self.time_budget = time_budget
        self.fixed_epochs = fixed_epochs
        
        # Dicionário para armazenar a quantidade de épocas calculadas para a PRÓXIMA rodada
        # Mapeia: Client ID (cid) -> num_epochs
        self.next_round_epochs = {}
        
        super().__init__(
            fraction_fit=1,
            fraction_evaluate=0.5,
            min_fit_clients=num_clients,
            min_evaluate_clients=num_clients,
            min_available_clients=num_clients,
            fit_metrics_aggregation_fn=weighted_average,
            initial_parameters=parameters,
        )

    def configure_fit(self, server_round, parameters, client_manager):
        # 1. Obtém as configurações padrão (lista de clientes selecionados)
        config_fit_results = super().configure_fit(server_round, parameters, client_manager)
        
        # 2. Injeta as instruções (num_epochs) para os clientes ANTES do treino
        for client_proxy, fit_ins in config_fit_results:
            # Na rodada 1, usa um valor padrão (ex: fixed_epochs / num_clients). 
            # Nas próximas, usa o valor calculado no aggregate_fit da rodada anterior.
            epochs = self.next_round_epochs.get(
                client_proxy.cid, 
                self.fixed_epochs / self.num_clients
            )
            fit_ins.config["num_epochs"] = epochs
            
        return config_fit_results

    def aggregate_fit(self, server_round: int, results, failures):
        if not results:
            return super().aggregate_fit(server_round, results, failures)

        if self.num_min_epochs == 0:
            for client_proxy, _ in results:
                self.next_round_epochs[client_proxy.cid] = self.fixed_epochs / self.num_clients
        else:
            # 1. Lê os reports dos clientes APÓS o treino direto da memória
            reports_list = []
            cid_list = []
            
            for client_proxy, fit_res in results:
                # fit_res.metrics contém exatamente o dicionário que o cliente retornou
                reports_list.append(fit_res.metrics)
                cid_list.append(client_proxy.cid)

            # 2. Executa o Otimizador
            self.optimizer = FlOptimizer(
                reports_list,
                self.num_min_epochs,
                self.time_budget,
                self.fixed_epochs,
            )
            clients_rounds = self.optimizer.solve()
            print(f"Round {server_round} - Computed epochs for clients: {clients_rounds}")
            # self.optimizer._report(force_print=True) # Descomente se quiser os logs do solver

            # 3. Calcula e salva os resultados para serem enviados na PRÓXIMA rodada
            list_of_selected_clients = []
            for idx, num_epochs in enumerate(clients_rounds):
                total = num_epochs + (self.fixed_epochs / self.num_clients)
                cid = cid_list[idx]
                
                self.next_round_epochs[cid] = total
                
                if total > 0:
                    list_of_selected_clients.append(cid)
                    
            print(f"Round {server_round} - Selected clients for next round: {list_of_selected_clients}")
        
        # CORREÇÃO: Filtrar os resultados de clientes que não treinaram (num_examples == 0)
        # Isso garante que clientes que receberam 0 épocas não quebrem o FedAvg
        valid_results = [
            (client_proxy, fit_res) 
            for client_proxy, fit_res in results 
            if fit_res.num_examples > 0
        ]

        if not valid_results:
            print(f"Round {server_round} - Nenhum resultado válido para agregar (todos num_examples == 0).")
            # Se ninguém treinou, não podemos agregar. Retornamos None.
            return None, {}
        
        # 4. Continua com a agregação padrão dos pesos do modelo (FedAvg)
        return super().aggregate_fit(server_round, valid_results, failures)

if __name__ == "__main__":

    num_clients = int(sys.argv[1])
    fixed_epochs = int(sys.argv[2])
    variable_epochs = int(sys.argv[3])

    print("Config")
    print(f"Num clients = {num_clients}")
    print(f"Fixed epochs = {fixed_epochs}")
    print(f"Variable epochs = {variable_epochs}")

    config = ServerConfig(num_rounds=5)

    try:
        start_server(
            server_address="0.0.0.0:7891",
            config=config,
            strategy=ModFedAvg(
                MLP(),
                num_min_epochs=variable_epochs,
                time_budget=60,
                fixed_epochs=fixed_epochs,
                num_clients=num_clients,
            ),
        )
    except ValueError as e:
        print(e)