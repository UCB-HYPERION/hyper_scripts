import aipy
import numpy as np

def get_aa(freqs):
    LAT = 37.2314 # degrees N
    LON = -118.2941 # degrees W

    FQ0 = 0.075
    LAM0 = aipy.const.c / (FQ0 * 1e9) # cm
    BL_NS = LAM0 / 2. * aipy.const.len_ns

    ANTPOS = np.array([
        [0., 0, 0],
        [0., BL_NS, 0],
    ])

    bm = aipy.fit.Beam(freqs)
    ants = [aipy.fit.Antenna(ANTPOS[i][0], ANTPOS[i][1], ANTPOS[i][2], bm) for i in range(2)]
    aa = aipy.fit.AntennaArray((str(LAT),str(LON)), ants)
    return aa

from aipy.cal import get_catalog
