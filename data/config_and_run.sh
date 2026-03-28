#!/bin/bash

# Define a estrutura de diretórios em um array
directories=(
    "MNIST"
    "MNIST/private_dataloaders_clear"
    "MNIST/private_dataloaders"
    "MNIST/public_dataloaders"
)

# Cria os diretórios caso não existam
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        # A flag -p garante que diretórios pais também sejam criados, se necessário
        mkdir -p "$dir"
        echo "Directory created: $dir"
    else
        echo "Directory already exists: $dir"
    fi
done

# Define o arquivo a ser criado
file_path="MNIST/info"

# Cria o arquivo caso ele não exista
if [ ! -f "$file_path" ]; then
    touch "$file_path"
    echo "File created: $file_path"
else
    echo "File already exists: $file_path"
fi

sudo docker compose -f compose.yaml up --build