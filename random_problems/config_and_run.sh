#!/bin/bash

if [ -z "$1" ]; then
  echo "Erro: Você precisa informar o número de clientes."
  echo "Uso correto: bash config_and_run.sh <numero_de_clientes>"
  exit 1
fi

mkdir -p logs
rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

sudo env NUM_CLIENTS=$1 docker compose up --build 

rm -rf wf_solver

cat logs/logs.txt