#!/bin/bash

set -e

VERSIONS=(3.5.1 3.6.2 3.7.2)

for v in "${VERSIONS[@]}"; do
    if pyenv versions | grep -E "^ *$v\$" > /dev/null; then
        echo Python $v already installed
    else
        echo Installing Python $v
        pyenv install $v
    fi

    [[ -e ve_$v ]] || virtualenv --python ~/.pyenv/versions/$v/bin/python ve_$v
done
