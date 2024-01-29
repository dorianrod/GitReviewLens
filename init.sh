#!/bin/bash

# creation of .env file
cp .env.example .env
# creation of transcoders.json file
cp ./postgres/transco/transcoders.json.example ./postgres/transco/transcoders.json 
# installation of python dependencies
python3 -m venv .venv
. .venv/bin/activate && pip install -r requirements.txt
# cloning
make clone_repositories