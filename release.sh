#!/bin/sh
THISDIR="$(cd "$(dirname "$0")"; pwd)"
python3 "$THISDIR/setup.py" sdist bdist
version="$(python "$THISDIR/setup.py" --version)"
twine upload "$@" "$THISDIR/dist/aio_task_bound_context-$version.tar.gz"
