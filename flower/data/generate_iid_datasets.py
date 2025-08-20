import torch
import torchvision
import configparser
import pathlib
from math import floor

GLOBAL_INFO_FOR_REPORT = {
    "dataset_name":None,
    "num_clients":None,
    "samples_per_client":None,
    "train_samples_per_client":None,
    "test_samples_per_client":None,
    "public_samples":None,
    "encryption":None
}

def write_report(file_name):
    report_content = f"""
    {GLOBAL_INFO_FOR_REPORT["dataset_name"]} IID data info

    Num clients = {GLOBAL_INFO_FOR_REPORT["num_clients"]}

    Samples per client = {GLOBAL_INFO_FOR_REPORT["samples_per_client"]}
    Train samples per client = {GLOBAL_INFO_FOR_REPORT["train_samples_per_client"]}
    Test samples per client = {GLOBAL_INFO_FOR_REPORT["test_samples_per_client"]}
    
    Public samples (for test at server) = {GLOBAL_INFO_FOR_REPORT["public_samples"]}

    Encryption with Gramine key = {GLOBAL_INFO_FOR_REPORT["encryption"]}
    """
    
    with open(file_name, 'w') as file:
        file.write(report_content.strip())  # Strip removes any leading/trailing whitespace

    print(report_content)
    print(f"This report has been written to {file_name}")

def fetch_mnist_dataset(do_download, data_path, rotation_angle_range=90):
    transform = torchvision.transforms.Compose([
        torchvision.transforms.RandomRotation(degrees=rotation_angle_range),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.1307,), (0.3081,))
    ])
    
    # Emulate a system call inside Gramine, which degrades performance
    train_data = torchvision.datasets.MNIST(
        data_path, train=True, download=do_download, transform=transform
    )
    test_data = torchvision.datasets.MNIST(
        data_path, train=False, download=do_download, transform=transform
    )

    GLOBAL_INFO_FOR_REPORT['dataset_name'] = 'MNIST'
    GLOBAL_INFO_FOR_REPORT['public_samples'] = len(test_data)

    return train_data, test_data

def fetch_cifar10_dataset(do_download, data_path):
    transform_train = torchvision.transforms.Compose([
        torchvision.transforms.RandomCrop(32, padding=4),
        torchvision.transforms.RandomHorizontalFlip(),
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    transform_test = torchvision.transforms.Compose([
        torchvision.transforms.ToTensor(),
        torchvision.transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ])

    # Emulate a system call inside Gramine, which degrades performance
    train_data = torchvision.datasets.CIFAR10(
        data_path, train=True, download=do_download, transform=transform_train
    )
    test_data = torchvision.datasets.CIFAR10(
        data_path, train=False, download=do_download
    )

    sample, _ = test_data[1]
    sample.show()
    input()

    GLOBAL_INFO_FOR_REPORT['dataset_name'] = 'CIFAR10'
    GLOBAL_INFO_FOR_REPORT['public_samples'] = len(test_data)

    return train_data, test_data

def iid_partition_loader(data, bsz=10, n_clients=100, train_fraction=0.8):
    m = len(data)
    assert m % n_clients == 0 # Must be divisible
    m_per_client = m // n_clients 
    #assert m_per_client % bsz == 0
    assert train_fraction < 1
    test_fraction = 1-train_fraction

    GLOBAL_INFO_FOR_REPORT['num_clients'] = n_clients
    GLOBAL_INFO_FOR_REPORT['samples_per_client'] = m_per_client
    
    clients_data = torch.utils.data.random_split(
        data,
        [m_per_client for _ in range(n_clients)]
    )

    clients_trainloader = []
    clients_testloader = []
    for client_data in clients_data:
        num_train_samples = floor(train_fraction*len(client_data))
        num_test_samples = len(client_data) - num_train_samples
        client_trainset, client_testset = torch.utils.data.random_split(client_data, [num_train_samples, num_test_samples])
        client_trainloader = torch.utils.data.DataLoader(client_trainset, batch_size=bsz, shuffle=True)
        client_testloader = torch.utils.data.DataLoader(client_testset, batch_size=bsz, shuffle=True)
        clients_trainloader.append(client_trainloader)
        clients_testloader.append(client_testloader)

    GLOBAL_INFO_FOR_REPORT['train_samples_per_client'] = round(m_per_client * train_fraction)
    GLOBAL_INFO_FOR_REPORT['test_samples_per_client'] = m_per_client - GLOBAL_INFO_FOR_REPORT['train_samples_per_client']

    return clients_trainloader, clients_testloader

def generate_data(
    train_data,
    test_data,
    private_data_path,
    public_data_path,
    train_batch_size,
    test_batch_size,
    num_partitions,
    num_used_clients,
    train_fraction
):

    train_loaders_list, local_test_loaders_list = iid_partition_loader(
        train_data, bsz=train_batch_size, n_clients=num_partitions, train_fraction=train_fraction)
    pathlib.Path(private_data_path).mkdir(parents=True, exist_ok=True)
    pathlib.Path(public_data_path).mkdir(parents=True, exist_ok=True)
    for i, train_loader in enumerate(train_loaders_list[:num_used_clients]):
        torch.save(train_loader,"{p}/client_{i}_trainloader.pth".format(i=i,p=private_data_path))
    for i, test_loader in enumerate(local_test_loaders_list[:num_used_clients]):
        torch.save(test_loader,"{p}/client_{i}_testloader.pth".format(i=i,p=private_data_path))
    global_test_loader = torch.utils.data.DataLoader(test_data, batch_size=test_batch_size, shuffle=False)
    torch.save(global_test_loader, "{p}/server_testloader.pth".format(p=public_data_path))

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    base_path = str(pathlib.Path().resolve())

    if(config.get('dataset','dataset') == "mnist"):
        if(config.get('exec_mode','exec_mode') == "gramine"):
            GLOBAL_INFO_FOR_REPORT['encryption'] = True
            data_path = "/data"
            public_data_path = "/data/MNIST/public_dataloaders"
            private_data_path = "/data/MNIST/private_dataloaders"
            report_path = "/data/MNIST"
            do_download = False
        else:
            GLOBAL_INFO_FOR_REPORT['encryption'] = False
            data_path = base_path
            public_data_path = base_path + "/MNIST/public_dataloaders"
            private_data_path = base_path + "/MNIST/private_dataloaders_clear"
            report_path = base_path + "/MNIST"
            do_download = config.getboolean('dataset','download')

    elif(config.get('dataset','dataset') == "cifar10"):
        if(config.get('exec_mode','exec_mode') == "gramine"):
            GLOBAL_INFO_FOR_REPORT['encryption'] = True
            data_path = "/data/CIFAR10"
            public_data_path = "/data/CIFAR10/public_dataloaders"
            private_data_path = "/data/CIFAR10/private_dataloaders"
            report_path = "/data/CIFAR10"
            do_download = False
        else:
            GLOBAL_INFO_FOR_REPORT['encryption'] = False
            data_path = base_path + "/CIFAR10"
            public_data_path = base_path + "/CIFAR10/public_dataloaders"
            private_data_path = base_path + "/CIFAR10/private_dataloaders_clear"
            report_path = base_path + "/CIFAR10"
            do_download = config.getboolean('dataset','download')

    if(config.get('dataset','dataset') == "mnist"):
        train_data, test_data = fetch_mnist_dataset(do_download,data_path)    
    elif(config.get('dataset','dataset') == "cifar10"):
        train_data, test_data = fetch_cifar10_dataset(do_download,data_path)       

    generate_data(
        train_data,
        test_data,
        private_data_path,
        public_data_path,
        config.getint('dataset','train_batch_size'),
        config.getint('dataset','server_test_batch_size'),
        config.getint('dataset','num_partitions'),
        config.getint('dataset','num_used_clients'),
        config.getfloat('dataset','train_fraction')
    )

    write_report(report_path+"/info")
