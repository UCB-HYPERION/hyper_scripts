#! /usr/bin/env python
import aipy, cPickle, astropy.time
import sys

for filename is sys.argv[1:]:
    f = open(filename)
    pkl = cPickle.load(f)
    times = pkl['times']
    jds = [astropy.time.Time(t, format='unix').jd for t in times]
