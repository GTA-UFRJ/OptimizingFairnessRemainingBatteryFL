from flwr.client import NumPyClient, start_client
from task import *
import sys
from random import randint
import json

# Define FlowerClient and client_fn
class FlowerClient(NumPyClient):
    def __init__(self) -> None:
        super().__init__()
        self.generate_random_client()

    def generate_random_client(self):
        battery_mAh = randint(1900,2200)
        battery_soc = randint(10,40)
        num_batches = randint(10,20)
        cpu_GHz = randint(28,32)
        ci_est = randint(24,36)*1e6
        gamma_est = randint(50,55) * 1e-29
        p_down_avg = 200e-6
        charging = False
        upload_Mbps = randint(40,60) 
        download_Mbps = upload_Mbps
        initial_report = {
            "battery_mAh":battery_mAh,
            "battery_soc":battery_soc,
            "num_batches":num_batches,
            "cpu_GHz":cpu_GHz,
            "ci_est":ci_est,
            "gamma_est":gamma_est,
            "p_down_avg":p_down_avg,
            "charging":charging,
            "upload_Mbps":upload_Mbps,
            "download_Mbps":download_Mbps
        }
        with open(f"initial_clients/client_{client_id}_to_server.json",'wb') as f:
            json.dump(initial_report,f)
        self.report = initial_report

    def create_client_report(self):
        Emax = self.report["battery_mAh"]* 1e-3 * 3600 * 3.7
        Eo = self.report["battery_soc"] * Emax / 100
        f = self.report["cpu_GHz"] * 1e12
        epsilon = self.report['num_batches']*self.report["ci_est"]*self.report["gamma_est"]*f*f
        E = Eo - epsilon*self.epochs
        self.report["battery_soc"] = 100*(E/Emax)
        with open(f"reports/client_{client_id}_to_server.json",'wb') as f:
            json.dump(self.report,f)

    def read_server_report(self):
        try:
            with open(f"reports/server_to_client_{client_id}.json",'rb') as f:
                self.epochs = json.load(f)["num_epochs"]
        except:
            self.epochs = 10

    def fit(self, parameters, config):
        set_weights(net, parameters)
        self.read_server_report()
        results = train(net, trainloader, testloader, epochs=self.epochs, batches=self.report["num_batches"])
        self.create_client_report()
        return get_weights(net), len(results["num_samples"]), results

    def evaluate(self, parameters, config):
        set_weights(net, parameters)
        loss, accuracy = test(net, testloader)
        return loss, len(testloader.dataset), {"accuracy": accuracy}

if __name__ == "__main__":

    net = MLP()
    client_id = int(sys.argv[1])
    trainloader, testloader = load_data("data/private_dataloaders_clear",client_id)

    start_client(
        server_address="127.0.0.1:8080",
        client=FlowerClient().to_client(),
    )    
    
