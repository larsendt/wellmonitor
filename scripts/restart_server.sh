#!/bin/bash

echo "Restarting"
./stop_server.sh && sleep 1 && ./start_server.sh
