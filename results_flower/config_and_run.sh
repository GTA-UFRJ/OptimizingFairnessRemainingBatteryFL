#!/bin/bash
rm -rf --interactive=never figures 
mkdir figures

rm -rf --interactive=never logs 
cp -r ../flower/logs .

rm -rf --interactive=never processed
mkdir processed

sudo docker compose -f compose.yaml up --build --force-recreate --remove-orphans 

rm -rf --interactive=never logs 