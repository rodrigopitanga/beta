#!/bin/bash
WORKERS=$(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 ))
echo "WORKERS: ${WORKERS}"

if [ ! -z ${WSGI_DEBUG} ]; then
	GUNICORN_LOG="--log-level DEBUG"
fi

cd ${APP_HOME}
source venv/bin/activate
echo "VirtualEnv: $VIRTUAL_ENV"
gunicorn -w ${WORKERS} -b 0.0.0.0:8000 ${GUNICORN_LOG} --capture-output apiserver.wsgi:app