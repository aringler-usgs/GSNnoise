#!/usr/bin/env python

import glob
import sys

import numpy as np

from obspy.signal.spectral_estimation import get_NLNM
import matplotlib.pyplot as plt

from multiprocessing import Pool

debug = True


# Grab the NLNM and get power and per in the microseism band
minper = 5.
maxper = 10.

per, NLNM = get_NLNM()

micNLNM = NLNM[(minper <= per) & (per <= maxper)]
micper = per[(minper <= per) & (per <= maxper)]




fDead = open('DeadChannels','w')

def checkifdead(curfile):
    try:

        with open(curfile,'r') as f:
            staper=[]
            stapow=[]
            for line in f:    
                line = (line.strip()).split(',')
                if (1./float(line[1]) >= minper) and (1./float(line[1]) <= maxper):
                    staper.append(1./float(line[1]))
                    stapow.append(float(line[0]))
        staper = np.asarray(staper)
        stapow = np.asarray(stapow)
        NLNMinterp = np.interp(1./staper,1./micper,micNLNM)
        #plt.figure()
        #p1=plt.semilogx(micper,micNLNM)
        #p2=plt.semilogx(staper,stapow,'k')
        #p3=plt.semilogx(staper,NLNMinterp,'r')
        #plt.show()
        dbdiff = 1./float(len(NLNMinterp))*sum(stapow-NLNMinterp)
        if dbdiff <= 0.:
            fDead.write(curfile + ' is dead with dB difference ' + str(dbdiff) + '\n')
    
    except:
        print curfile + ' is bad'

    return

pool = Pool(10)
for year in range(1989,2016):
    for days in range(1,367):
        print 'On ' + str(year) + ' ' + str(days).zfill(3)
        files = glob.glob('/TEST_ARCHIVE/PSDS/*/' + str(year) + '/PSD*' + str(days).zfill(3)) 
        pool.map(checkifdead,files)










