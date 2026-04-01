#!/bin/bash

mkdir -p logs
rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

sudo env NUM_CLIENTS=20 docker compose up --build 

rm -rf wf_solver

cat logs/logs.txt

rm -rf logs/*