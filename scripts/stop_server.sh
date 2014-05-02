#!/bin/bash

pid=`pgrep -f "python ../webpy/wellmonitor.py"`
if [ $pid ]
then
    echo "Killed $pid"
    kill $pid
else
    echo "No process to kill"
    exit 0
fi
