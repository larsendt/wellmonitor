#!/usr/bin/env python

import wellmonitor as wm
import random

data = map(lambda x: random.randint(0,1), range(5))
wm.add_reading(*data)
