#!/usr/bin/env bash


REALLY_RUN="${1:-false}"

sudo apt-get update

if [ "$REALLY_RUN" == "false" ]; then 
    xargs -a apt.txt sudo apt-get install -y --dry-run
    exit 0
else
    xargs -a apt.txt sudo apt-get install -y
fi
