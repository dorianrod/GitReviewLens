#!/bin/bash

for directory in /repos/*; do
    if [ -d "$directory" ]; then
        cd "$directory"
        git config --global --add safe.directory "/repos/$directory"
        cd -
    fi
done
