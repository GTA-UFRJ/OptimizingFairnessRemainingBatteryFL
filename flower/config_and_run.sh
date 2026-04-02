#!/bin/bash
FIXED_ROUNDS=$1
VARIABLE_ROUNDS=$2
NUM_RUNS="${3:4}"

LOGDIR=logs/fixed_${FIXED_ROUNDS}_variable_${VARIABLE_ROUNDS}
mkdir -p $LOGDIR

rm -rf --interactive=never initial_clients 
mkdir initial_clients

rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

rm -rf --interactive=never MNIST
cp -r ../data/MNIST .

for i in $(seq 1 $NUM_RUNS); do
    sudo FIXED_ROUNDS=$FIXED_ROUNDS VARIABLE_ROUNDS=$VARIABLE_ROUNDS RUN=$i docker compose -f compose.yaml up --build
    cat $LOGDIR/${i}_server.logs
    sudo docker compose -f compose.yaml down
done

rm -rf ./wf_solver
rm -rf ./MNIST
