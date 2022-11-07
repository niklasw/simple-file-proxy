#!/usr/bin/sh

LOG_DIR="logs"
PORT=5080

function already_running()
{
    if ss -tulpn | grep -q ":$PORT\>"
    then
        echo "Server seems already be running on port $PORT"
        exit 1
    fi
}

if [[ "$1" == stop ]]
then
    SPID=$(<"$LOG_DIR/PID")
    if kill $SPID
    then
        echo killed $SPID
    fi
    exit 0
fi

already_running
source venv/bin/activate
./server.py $PORT > $LOG_DIR/server.log 2>&1 &

