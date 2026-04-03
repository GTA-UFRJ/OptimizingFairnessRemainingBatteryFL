from typing import List, Tuple
from pathlib import Path
from flwr.common import Metrics, ndarrays_to_parameters, FitIns
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
        # 1. Obtém as configurações padrão
        config_fit_results = super().configure_fit(server_round, parameters, client_manager)
        
        # Criamos uma nova lista para não sobrescrever a referência padrão
        custom_config_fit_results = []
        
        # 2. Injeta as instruções exclusivas para cada cliente
        for client_proxy, fit_ins in config_fit_results:
            
            epochs = self.next_round_epochs.get(
                client_proxy.cid, 
                (self.num_min_epochs + self.fixed_epochs) / self.num_clients
            )
            
            # O SEGREDO AQUI: Criar uma cópia isolada da config padrão
            client_config = fit_ins.config.copy()
            client_config["num_epochs"] = epochs
            
            # Criar um NOVO objeto FitIns amarrado aos parâmetros originais, mas com a config individual
            client_fit_ins = FitIns(parameters=fit_ins.parameters, config=client_config)
            
            custom_config_fit_results.append((client_proxy, client_fit_ins))

        print(f"Round {server_round} - Configured clients with epochs: {[fit_ins.config['num_epochs'] for _, fit_ins in custom_config_fit_results]}")
        
        return custom_config_fit_results

    def aggregate_fit(self, server_round: int, results, failures):
        
        if self.num_min_epochs == 0:
            for client_proxy, _ in results:
                self.next_round_epochs[client_proxy.cid] = self.fixed_epochs / self.num_clients
            return super().aggregate_fit(server_round, results, failures)

        # 1. Lê os reports dos clientes APÓS o treino
        reports_list = []
        cid_list = []

        print(f"Round {server_round} - Received reports from clients: {[fit_res.metrics for _, fit_res in results]}")
        
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
        # self.optimizer._report(force_print=True) # Descomente se quiser os logs do solver

        # 3. Calcula e salva os resultados para serem enviados na PRÓXIMA rodada
        for idx, num_epochs in enumerate(clients_rounds):
            cid = cid_list[idx]
            self.next_round_epochs[cid] = num_epochs + (self.fixed_epochs / self.num_clients)

        print(f"Round {server_round} - Final epochs to be sent to clients in next round: {self.next_round_epochs}")
                
        print(f"Selected clients: {[cid for cid, total in self.next_round_epochs.items() if total > 0]}")
        
        # Agrega apenas os clientes que receberam mais de 0 épocas na rodada atual. 
        # Os outros serão ignorados (mas continuam sendo considerados no cálculo do otimizador para as próximas rodadas).

        valid_results = [
            (client_proxy, fit_res) 
            for client_proxy, fit_res in results 
            if fit_res.num_examples > 0
        ]

        print(f"Round {server_round} - Valid clients for aggregation in current round (num_examples > 0): {[client_proxy.cid for client_proxy, _ in valid_results]}")

        assert len(valid_results) > 0, "No valid client results to aggregate. All clients received 0 epochs."
        
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