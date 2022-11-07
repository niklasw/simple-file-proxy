#!/usr/bin/sh

LOG_DIR="logs"
PORT=5080

if [[ "$1" == stop ]]
then
    SPID=$(<"$LOG_DIR/PID")
    if kill $SPID
    then
        echo killed $SPID
    fi
    exit 0
fi

source venv/bin/activate
./server.py $PORT > $LOG_DIR/server.log 2>&1 &

