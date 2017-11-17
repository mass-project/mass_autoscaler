#!/bin/bash
sudo docker build -t size35 ./image
sudo docker stack deploy -c docker-compose.yml size35serv
