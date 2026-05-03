#!/bin/bash

# 1. Validação de segurança: exige os dois primeiros argumentos
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Erro: Faltam argumentos!"
    echo "Uso: ./specific_run.sh <FIXED_ROUNDS> <VARIABLE_ROUNDS> <RUN_ID>"
    echo "Exemplo: ./specific_rin.sh 2 8 1"
    exit 1
fi

# 2. Definição de Variáveis (Substitui o .env)
FIXED_ROUNDS=$1
VARIABLE_ROUNDS=$2
RUN_ID=$3
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
export RUN=$RUN_ID

# Derruba qualquer resquício antes de começar
sudo -E docker compose -f compose.yaml down --remove-orphans

echo "========================================"
echo " Iniciando etapa de build dos containers"
echo "========================================"

# 4. Faz o build dos containers apenas da primeira vez.
# O operador '!' inverte o resultado. Se o build falhar, entra no 'if' e encerra o script.
if ! sudo -E docker compose -f compose.yaml build; then
    echo "[Erro] Problema detectado durante o build. Interrompendo a execução do script."
    exit 1
fi

echo "Build concluído com sucesso!"

export RUN=$RUN_ID

echo "========================================"
echo " Iniciando Experimento $RUN_ID          "
echo "========================================"

# Sobe os containers SEM a flag --build
sudo -E docker compose -f compose.yaml up --force-recreate --remove-orphans -d

# Espera o container do servidor (flower_server) terminar de rodar
echo "Aguardando o servidor finalizar a execução do experimento"
sudo docker wait flower_server

echo " "
echo "--> Visualizando log do servidor (Execução $RUN_ID):"
cat "$LOGDIR/${RUN_ID}_server.logs"

# O comando down avalia o compose.yaml, logo, também precisa do sudo -E
sudo -E docker compose -f compose.yaml down --remove-orphans

# 6. Limpeza final
rm -rf ./wf_solver
rm -rf ./MNIST

echo "========================================"
echo "  Bateria de testes finalizada!         "
echo "========================================"