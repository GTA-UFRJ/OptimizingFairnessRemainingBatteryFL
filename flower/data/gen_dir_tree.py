import os

def create_directories():
    # Define the directory structure
    directories = [
        "MNIST",
        "MNIST/private_dataloaders_clear",
        "MNIST/private_dataloaders",
        "MNIST/public_dataloaders",
        "CIFAR10",
        "CIFAR10/cifar-10-batches-py",
        "CIFAR10/private_dataloaders_clear",
        "CIFAR10/private_dataloaders",
        "CIFAR10/public_dataloaders",
    ]

    # Create directories if they do not exist
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory created: {directory}")
        else:
            print(f"Directory already exists: {directory}")

    # Define the files to be created
    files = [
        "MNIST/info",
        "CIFAR10/info",
    ]

    # Create files if they do not exist
    for file_path in files:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass  # Create an empty file
            print(f"File created: {file_path}")
        else:
            print(f"File already exists: {file_path}")

if __name__ == "__main__":
    create_directories()
