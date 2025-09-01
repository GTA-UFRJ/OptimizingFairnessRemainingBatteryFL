#!/bin/bash

NUM_CLIENTS=$1
python3 -um flower.fed_server $NUM_CLIENTS > flower/logs/server.logs 2>&1 &
echo "kill $!"
sleep 2
for i in $(seq 0 $(( NUM_CLIENTS - 1 )) ); do
  python3 -um flower.fed_client $i > flower/logs/client$i.logs 2>&1 &
  echo "kill $!"
done