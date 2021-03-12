#!/bin/bash

help() {
    echo -e "Usage:\n\tsetup.sh [command]\n\ncommand:\n\tlocal - Set up the running environment locally.\n\timage - Set up the running environment in a Docker image.\n"
}

if [ $1x = "localx" ]; then
    cd setup
    apt-get update
    apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev python3-pip python3-dev
    pip3 install pyopenssl ndg-httpsclient pyasn1
    tar -zxvf ta-lib-0.4.0-src.tar.gz
    (
        cd ta-lib/
        ./configure --prefix=/usr && make && make install
    )
    (
        cd ../
        pip3 install -r requirements.txt
    )
elif [ $1x = "imagex" ]; then
    docker build -t cryptopy:latest -f setup/Dockerfile .
else
    help
fi
