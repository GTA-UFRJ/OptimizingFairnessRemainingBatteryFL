#!/bin/bash

# 1. Validação de segurança: exige os dois primeiros argumentos
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Erro: Faltam argumentos!"
    echo "Uso: ./run_experiments.sh <FIXED_ROUNDS> <VARIABLE_ROUNDS> [NUM_RUNS]"
    echo "Exemplo: ./run_experiments.sh 2 8 5"
    exit 1
fi

# 2. Definição de Variáveis (Substitui o .env)
FIXED_ROUNDS=$1
VARIABLE_ROUNDS=$2
NUM_RUNS="${3:-3}" # Se $3 for vazio, assume 3
NUM_CLIENTS=5     # Variável fixa

LOGDIR="logs/fixed_${FIXED_ROUNDS}_variable_${VARIABLE_ROUNDS}"
mkdir -p "$LOGDIR"

# 3. Preparação do ambiente (Limpeza e cópia)
rm -rf --interactive=never initial_clients 
mkdir initial_clients

rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

rm -rf --interactive=never MNIST
cp -r ../data/MNIST .

# Exportando as variáveis globais do experimento para que o sudo -E as enxergue
export NUM_CLIENTS=$NUM_CLIENTS
export FIXED_ROUNDS=$FIXED_ROUNDS
export VARIABLE_ROUNDS=$VARIABLE_ROUNDS
export RUN=1

sudo -E docker compose -f compose.yaml down

# 4. Loop de Execução
for i in $(seq 1 $NUM_RUNS); do
    # Exporta o RUN da iteração atual
    export RUN=$i
    
    echo "========================================"
    echo " Iniciando Experimento $i de $NUM_RUNS"
    echo "========================================"

    # Usamos sudo -E para o Docker herdar as variáveis exportadas acima
    sudo -E docker compose -f compose.yaml up --build --force-recreate --remove-orphans -d

    # Espera o container do servidor (flower_server) terminar de rodar
    echo "Aguardando o servidor finalizar a execução do experimento $i..."
    sudo docker wait flower_server
    
    echo " "
    echo "--> Visualizando log do servidor (Execução $i):"
    cat "$LOGDIR/${i}_server.logs"
    
    # O comando down também avalia o compose.yaml, logo, ele também precisa do sudo -E
    sudo -E docker compose -f compose.yaml down --remove-orphans
done

# 5. Limpeza final
rm -rf ./wf_solver
rm -rf ./MNIST

echo "========================================"
echo "  Bateria de testes finalizada!         "
echo "========================================"