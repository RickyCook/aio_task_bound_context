#!/bin/bash

set -e

THISDIR="$(cd "$(dirname "$0")"; pwd)"

"$THISDIR/tests_setup.sh"

for ve in $(ls "$THISDIR" | grep -E '^ve_'); do
    "$THISDIR/$ve/bin/python" ./test.py
done
