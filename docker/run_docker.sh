#!/bin/bash

xhost +local:docker || true

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"/workspace

echo "[!] your /workspace directory symlinked to: $ROOT_DIR" 

docker run  -ti --rm \
            -e "DISPLAY" \
            -e "QT_X11_NO_MITSHM=1" \
            -v "/tmp/.X11-unix:/tmp/.X11-unix:rw" \
            -e XAUTHORITY \
            -v /dev:/dev \
            -v $ROOT_DIR/:/workspace \
            --net=host \
            --privileged \
            --name b_bot b_bot-img

