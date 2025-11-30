#!/usr/bin/env bash
docker stop subscriber-stack
docker rm subscriber-stack
docker rmi final_project_subscriber_stack:latest
docker ps -a
docker image ls