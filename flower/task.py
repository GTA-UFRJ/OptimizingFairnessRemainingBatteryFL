from collections import OrderedDict
from logging import INFO

import torch
import torch.nn as nn
import torch.nn.functional as F
from flwr.common.logger import log
from torch.utils.data import DataLoader
from torchvision.datasets import CIFAR10
from torchvision.transforms import Compose, Normalize, ToTensor

class MLP(nn.Module):
    def __init__(self):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(784, 200)
        self.fc2 = nn.Linear(200, 200)
        self.out = nn.Linear(200, 10)

    def forward(self, x):
        x = x.flatten(1) # [B x 784]
        x = F.relu(self.fc1(x)) # [B x 200]
        x = F.relu(self.fc2(x)) # [B x 200]
        x = self.out(x) # [B x 10]
        return x

def load_data(data_path,i=""):
    """Load CIFAR-10 (training and test set)."""
    trainloader = torch.load(f"{data_path}/client_{i}_trainloader.pth")
    testloader = torch.load(f"{data_path}/client_{i}_testloader.pth")
    return trainloader, testloader

def train(net, trainloader, valloader, epochs, batches):
    """Train the model on the training set."""
    log(INFO, "Starting training...")
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(net.parameters(), lr=0.001, momentum=0.9)
    net.train()
    for _ in range(epochs):
        num_samples = 0 
        for i, (images, labels) in enumerate(trainloader):
            images, labels = images, labels
            optimizer.zero_grad()
            loss = criterion(net(images), labels)
            loss.backward()
            optimizer.step()
            if i == batches:
                break
            num_samples += 1

    train_loss, train_acc = test(net, trainloader)
    val_loss, val_acc = test(net, valloader)

    results = {
        "train_loss": train_loss,
        "train_accuracy": train_acc,
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "num_samples":num_samples
    }
    return results


def test(net, testloader):
    """Validate the model on the test set."""
    criterion = torch.nn.CrossEntropyLoss()
    correct, loss = 0, 0.0
    with torch.no_grad():
        for images, labels in testloader:
            outputs = net(images)
            loss += criterion(outputs, labels).item()
            correct += (torch.max(outputs.data, 1)[1] == labels).sum().item()
    accuracy = correct / len(testloader.dataset)
    return loss, accuracy


def get_weights(net):
    return [val.cpu().numpy() for _, val in net.state_dict().items()]


def set_weights(net, parameters):
    params_dict = zip(net.state_dict().keys(), parameters)
    state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
    net.load_state_dict(state_dict, strict=True)
