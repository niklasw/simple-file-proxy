#!/usr/bin/sh

source venv/bin/activate
./server.py > server.log 2>&1 &

