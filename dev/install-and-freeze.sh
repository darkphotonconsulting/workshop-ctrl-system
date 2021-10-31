#!/usr/bin/env bash 

PYTHON="/usr/bin/python3.7"

install-and-freeze() {
    local pkg=$1

    if [ -z "$1" ]; then
        echo "usage: install-and-freeze <pkg name>"
        return 1
    fi

    local _ins="$PYTHON -m pip install $pkg"
    eval "$_ins"
    "$PYTHON" -m pip freeze | grep "$pkg" -i |tee -a requirements.txt
}



install-and-freeze "$@";