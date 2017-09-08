#! /usr/bin/env python
import aipy, cPickle, astropy.time
import sys
import numpy as np

BANDWIDTH = 0.125 # GHz
CALFILE = 'ovro_2ant_ew'

for filename in sys.argv[1:]:
    uv_filename = filename.replace('pkl','uv')
    print filename, '->', uv_filename
    f = open(filename)
    pkl = cPickle.load(f)
    times = np.array(pkl['times'])
    inttime = np.average(times[1:]-times[:-1])
    jds = [astropy.time.Time(t, format='unix').jd for t in times]
    # XXX setting this by hand because not in file
    NCHAN = pkl['data'][0]['xx'].size
    fqs = np.arange(0., BANDWIDTH, BANDWIDTH / NCHAN)
    aa = aipy.cal.get_aa(CALFILE, fqs)

    # make uv file
    uv = aipy.miriad.UV(uv_filename, status='new')
    uv._wrhd('obstype','mixed-auto-cross')
    uv._wrhd('history','HYPERION: created file.\n')
    uv.add_var('telescop','a'); uv['telescop'] = 'HYPERION'
    uv.add_var('operator','a'); uv['operator'] = 'HYPERION'
    uv.add_var('version' ,'a'); uv['version'] = '0.0.1'
    uv.add_var('epoch'   ,'r'); uv['epoch'] = 2000.
    uv.add_var('source'  ,'a'); uv['source'] = 'zenith'
    uv.add_var('latitud' ,'d'); uv['latitud'] = aa.lat
    uv.add_var('dec'     ,'d'); uv['dec'] = aa.lat
    uv.add_var('obsdec'  ,'d'); uv['obsdec'] = aa.lat
    uv.add_var('longitu' ,'d'); uv['longitu'] = aa.long
    uv.add_var('npol'    ,'i'); uv['npol'] = 1
    uv.add_var('nspect'  ,'i'); uv['nspect'] = 1
    uv.add_var('nants'   ,'i'); uv['nants'] = len(aa)
    uv.add_var('antpos'  ,'d')
    antpos = np.array([ant.pos for ant in aa], dtype=np.double)
    uv['antpos'] = antpos.transpose().flatten()
    uv.add_var('sfreq'   ,'d'); uv['sfreq'] = fqs[0]
    uv.add_var('freq'    ,'d'); uv['freq'] = fqs[0]
    uv.add_var('restfreq','d'); uv['restfreq'] = fqs[0]
    uv.add_var('sdf'     ,'d'); uv['sdf'] = fqs[1]-fqs[0]
    uv.add_var('nchan'   ,'i'); uv['nchan'] = fqs.size
    uv.add_var('nschan'  ,'i'); uv['nschan'] = fqs.size
    uv.add_var('inttime' ,'r'); uv['inttime'] = inttime
    # These variables just set to dummy values
    uv.add_var('vsource' ,'r'); uv['vsource'] = 0.
    uv.add_var('ischan'  ,'i'); uv['ischan'] = 1
    uv.add_var('tscale'  ,'r'); uv['tscale'] = 0.
    uv.add_var('veldop'  ,'r'); uv['veldop'] = 0.
    # These variables will get updated every spectrum
    uv.add_var('coord'   ,'d')
    uv.add_var('time'    ,'d')
    uv.add_var('lst'     ,'d')
    uv.add_var('ra'      ,'d')
    uv.add_var('obsra'   ,'d')
    uv.add_var('baseline','r')
    uv.add_var('pol'     ,'i')
    for jd,data in zip(jds, pkl['data']):
        aa.set_jultime(jd)
        lst = aa.sidereal_time()
        uv['lst'] = lst
        uv['ra'] = lst
        uv['obsra'] = lst
        uv['pol'] = aipy.miriad.str2pol['xx'] # XXX hardcoded
        v00 = data['xx']
        crd = aa.get_baseline(0,0)
        preamble = (crd, jd, (0,0))
        flags = np.zeros(fqs.size, dtype=np.int32)
        uv.write(preamble, v00, flags)
        v01 = data['xy']
        crd = aa.get_baseline(0,1)
        preamble = (crd, jd, (0,1))
        uv.write(preamble, v01, flags)
        v11 = data['yy']
        crd = aa.get_baseline(1,1)
        preamble = (crd, jd, (1,1))
        uv.write(preamble, v11, flags)
    del(uv)

