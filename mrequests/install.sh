#!/bin/bash
#
# Install mrequests to a MicroPython board

MODULES=('defaultdict.py' 'mrequests.py' 'urlencode.py')

for py in ${MODULES[*]}; do
    echo "Compiling $py to ${py%.*}.mpy"
    rshell --quiet\
        -b ${BAUD:-9600} \
        -p ${PORT:-/dev/ttyACM0} \
        cp "${py%.*}".mpy "${DESTDIR:-/pyboard}"
done

