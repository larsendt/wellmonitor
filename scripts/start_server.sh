#!/bin/bash

spawn-fcgi -d ../webpy -f ../webpy/wellmonitor.py -a 127.0.0.1 -p 55134
