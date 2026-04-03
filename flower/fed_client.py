from time import sleep

from flwr.client import NumPyClient, start_client
from task import *
import sys
from random import randint
import json

class FlowerClient(NumPyClient):
    def __init__(self) -> None:
        super().__init__()
        self.epochs = 1 # Inicialização padrão
        self.generate_random_client()

    def generate_random_client(self):
        battery_mAh = randint(1900, 2200)
        battery_soc = randint(10, 40)
        num_batches = randint(10, 20)
        cpu_GHz = randint(28, 32) / 10
        ci_est = randint(24, 36) * 1e10
        gamma_est = randint(50, 55) * 1e-38
        p_down_avg = 200e-6
        charging = False
        upload_Mbps = randint(40, 60)
        download_Mbps = upload_Mbps
        
        # Mantém o report inicial apenas na memória, sem salvar em JSON
        self.report = {
            "battery_mAh": battery_mAh,
            "battery_soc": battery_soc,
            "num_batches": num_batches,
            "cpu_GHz": cpu_GHz,
            "ci_est": ci_est,
            "gamma_est": gamma_est,
            "p_down_avg": p_down_avg,
            "charging": charging,
            "upload_Mbps": upload_Mbps,
            "download_Mbps": download_Mbps
        }

        with open(f"initial_clients/client_{client_id}.json",'w') as f:
            json.dump(self.report,f,indent=4)
        self.report = self.report
        print(f"battery_mAh:{battery_mAh}")

    def update_client_report(self):
        """Atualiza o estado da bateria após o treino (substitui o create_client_report)"""
        Emax = self.report['battery_mAh'] * 1e-3 * 3600 * 3.7
        print(f"Previous battery SoC: {self.report['battery_soc']:.2f}%")
        
        Eo = self.report['battery_soc'] * Emax / 100
        f = self.report['cpu_GHz'] * 1e12
        epsilon = self.report['num_batches'] * self.report['ci_est'] * self.report['gamma_est'] * f * f
        E = Eo - epsilon * self.epochs
        
        self.report['battery_soc'] = 100 * (E / Emax)
        print(f"New battery SoC: {self.report['battery_soc']:.2f}%")

    def fit(self, parameters, config):
        # 1. Lê a instrução do servidor (substitui o read_server_report)
        # O .get() garante que, se o servidor não enviar nada (ex: rodada 1), ele use 1 época
        self.epochs = config.get('num_epochs', 1) 
        print(f"Received instruction to train for {self.epochs} epochs")

        if self.epochs <= 0:
            print("Received 0 epochs, skipping training and returning current metrics.")
            return get_weights(net), 0, self.report.copy()  # Retorna os pesos atuais, 0 amostras e o relatório atual sem alterações

        # 2. Prepara e executa o treino
        set_weights(net, parameters)
        results = train(net, trainloader, testloader, epochs=self.epochs, batches=self.report['num_batches'])
        
        # 3. Atualiza o consumo de bateria na memória local
        self.update_client_report()
        
        # 4. Prepara as métricas para enviar de volta ao servidor
        # Combina os dados de hardware (self.report) com os resultados do treino (loss, accuracy, etc)
        metrics_to_send = self.report.copy()
        
        # Removemos chaves que não sejam int, float, bool ou str, caso existam no dict results
        for key, value in results.items():
            if isinstance(value, (int, float, bool, str)):
                metrics_to_send[key] = value

        # Retorna os pesos, a quantidade de amostras e o dicionário completo de métricas
        return get_weights(net), results.get('num_samples', len(trainloader.dataset)), metrics_to_send

    def evaluate(self, parameters, config):
        set_weights(net, parameters)
        loss, accuracy = test(net, testloader)
        print(f"Test accuracy: {accuracy}")
        return loss, len(testloader.dataset), {"accuracy": accuracy}

if __name__ == "__main__":
    net = MLP()
    client_id = int(sys.argv[1])
    trainloader, testloader = load_data("data/MNIST/private_dataloaders_clear", client_id)

    while True:
        try:
            sleep(10)
            start_client(
                server_address="172.17.0.1:7891",
                client=FlowerClient().to_client(),
            )
        except Exception as e:
            print(f"Connection error: {e}. Retrying in 10 seconds...")