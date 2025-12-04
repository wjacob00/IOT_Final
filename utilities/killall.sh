#!/usr/bin/env bash
docker stop subscriber-stack
docker rm subscriber-stack
docker rmi final_project_subscriber_stack:latest

docker stop publisher
docker rm publisher
docker rmi final_project_publisher:latest

docker stop react-ui
docker rm react-ui
docker rmi final_project_react-ui:latest

docker stop mqtt-broker
docker rm mqtt-broker
docker rmi eclipse-mosquitto:2 

docker ps -a
docker image ls