#!/bin/bash

min_minor=9

get_current_minor() {
    parts=($(python3 -V | awk '{ print $2 }' | tr '.' ' '))
    if [ $? -ne 0 ]; then
        echo 0
        return
    fi
    echo ${parts[1]}
}

help() {
    echo -e "Usage:\n\tsetup.sh [command]\n\ncommand:\n\tlocal - Set up the running environment locally.\n\timage - Set up the running environment in a Docker image.\n"
}

generate_dockerfile() {
    echo -e "FROM python:3.$min_minor-slim\nRUN mkdir /project\nWORKDIR /project\nCOPY . .\nRUN chmod u+x setup/setup.sh && ./setup/setup.sh local\nENTRYPOINT [ \"python3\" ]" >setup/Dockerfile
}

if [ $1x = "localx" ]; then
    cd setup
    apt-get update
    apt-get install -y --no-install-recommends build-essential libssl-dev libffi-dev
    minor=$(get_current_minor)
    echo "The minor version of current Python3 is $minor, require >= $min_minor" 
    if [ $minor -lt $min_minor ]; then
        echo "Trying to update Python3"
        apt-get install -y --no-install-recommends python3-dev python3-pip
    fi
    minor=$(get_current_minor)
    if [ $minor -lt $min_minor ]; then
        echo "ERROR: Failed to update Python, please install manually."
        exit 1
    fi
    apt-get clean
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
    generate_dockerfile
    docker build -t cryptopy:latest -f setup/Dockerfile .
else
    help
fi
