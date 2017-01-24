#!/bin/bash
docker login -e $DOCKER_EMAIL -u $DOCKER_USER -p $DOCKER_PASS
export REPO=openbeta/apiserver:latest
docker tag apiserver:latest $REPO
docker push $REPO
