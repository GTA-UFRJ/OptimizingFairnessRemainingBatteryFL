from typing import Callable, List, Tuple
from pathlib import Path
from flwr.common import FitRes, Metrics, MetricsAggregationFn, Parameters, ndarrays_to_parameters
from flwr.server import ServerConfig, start_server
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg
import json
from wf_solver import WaterFillingSolver
from client import Client

from flower.task import MLP, get_weights

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

class Optimizer(WaterFillingSolver):
    def __init__(self, reports_list, num_min_epochs: int, time_budget: float, fixed_epochs: int = 2):
        self._set_clients(reports_list, time_budget)
        super().__init__(self.clients_list, num_min_epochs, time_budget, thresh=1, is_log_active=True, fixed_epochs=fixed_epochs)

    def _set_clients(self, reports_list, time_budget):
        self.clients_list = []
        for report in reports_list:
            Emax = report["battery_mAh"]* 1e-3 * 3600 * 3.7
            Eo = report["battery_soc"] * Emax / 100
            f = report["cpu_GHz"] * 1e12
            self.clients_list.append(
                Client(
                    Eio=Eo, 
                    Bi=report["num_batches"], 
                    gamma_i=report["gamma_est"],
                    ci=report["ci_est"],
                    fi=f,
                    P_down_avg=report["p_down_avg"],
                    Pi=0,
                    max_time=time_budget,
                    ui=4*8/report["upload_Mbps"],
                    di=4*8/report["download_Mbps"],
                    is_log_active=True)
            )
            
class ModFedAvg(FedAvg):
    def __init__(self, net, num_min_epochs, time_budget, fixed_epochs, num_clients) -> None:
        self.num_clients = num_clients
        ndarrays = get_weights(net)
        parameters = ndarrays_to_parameters(ndarrays)
        self.num_min_epochs = num_min_epochs
        self.time_budget = time_budget
        self.fixed_epochs = fixed_epochs
        super().__init__(fraction_fit=1, fraction_evaluate=0.5, min_fit_clients=num_clients, min_evaluate_clients=num_clients, min_available_clients=num_clients, fit_metrics_aggregation_fn=weighted_average, initial_parameters=parameters)

    def read_clients_reports(self):
        self.received_reports_list = [None] * self.num_clients
        for file in Path("flower/reports").glob("*.json"):
            file = str(file)
            try:
                slices = file.split("_")
                client_id = int(slices[1])
                with open(file,'r') as f:
                    self.received_reports_list[client_id] = json.load(f)
            except:
                continue

    def generate_server_reports(self):
        clients_rounds = [self.optimizer.csi - r for r in self.optimizer.r_list]
        for client_id, num_epochs in enumerate(clients_rounds):
            with open(f"flower/reports/server_to_client_{client_id}.json",'w') as f:
                json.dump({"num_epochs":num_epochs},f)

    def aggregate_fit(self, server_round: int, results, failures):
        self.read_clients_reports()
        self.optimizer = Optimizer(self.received_reports_list, self.num_min_epochs, self.time_budget, self.fixed_epochs)
        self.optimizer.solve()
        self.generate_server_reports()
        self.optimizer
        return super().aggregate_fit(server_round, results, failures)

if __name__ == "__main__":

    config = ServerConfig(num_rounds=10)

    start_server(
        server_address="0.0.0.0:8080",
        config=config,
        strategy=ModFedAvg(MLP(),num_min_epochs=50,time_budget=40,fixed_epochs=2,num_clients=5),
    )
