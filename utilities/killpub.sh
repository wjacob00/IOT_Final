#!/usr/bin/env bash
docker stop publisher
docker rm publisher
docker rmi final_project_publisher:latest
docker ps -a
docker image ls