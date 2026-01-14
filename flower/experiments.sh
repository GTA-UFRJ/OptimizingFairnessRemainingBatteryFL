#!/bin/bash

path=$( dirname "$(realpath $0)" )
echo $path
NUM_CLIENTS=$1
FIXED_ROUNDS=$2
VARIABLE_ROUNDS=$3
LOGDIR=$path/logs_$( date +"%Y_%m_%d_%I_%M_%p" )
echo $LOGDIR
mkdir $LOGDIR
rm $path/reports/*
cd $path/..
mkdir $path/reports
mkdir $path/initial_clients
pwd
sleep 5
python3 -um flower.fed_server $NUM_CLIENTS $FIXED_ROUNDS $VARIABLE_ROUNDS 1 > $LOGDIR/server.logs 2>&1 &
echo "kill $!"
sleep 5
for i in $(seq 0 $(( NUM_CLIENTS - 1 )) ); do
  python3 -um flower.fed_client $i 5 > $LOGDIR/client$i.logs 2>&1 &
  echo "kill $!"
done