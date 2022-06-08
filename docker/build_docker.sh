#!/usr/bin/env bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
EXEC_PATH=$PWD

cd $ROOT_DIR

docker build -t b_bot-img -f $ROOT_DIR/docker/Dockerfile $ROOT_DIR \
                              --network=host \
                              --build-arg from=ubuntu:20.04
cd $EXEC_PATH