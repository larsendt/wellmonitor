#!/usr/bin/env python

import wellmonitor as wm
import random

data = map(lambda x: random.choice((0, 1, None)), range(5))
wm.add_reading(*data)
