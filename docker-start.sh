#!/bin/bash
WORKERS=$(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 ))
echo "WORKERS: ${WORKERS}"
gunicorn -w ${WORKERS} -b 127.0.0.1:8000 --log-level DEBUG --capture-output apiserver.wsgi:app