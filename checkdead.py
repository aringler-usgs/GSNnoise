#!/usr/bin/env python

import glob
import sys

import numpy as np

from obspy.signal.spectral_estimation import get_NLNM
import matplotlib.pyplot as plt

debug = True


# Grab the NLNM and get power and per in the microseism band
minper = 5.
maxper = 10.

per, NLNM = get_NLNM()

micNLNM = NLNM[(minper <= per) & (per <= maxper)]
micper = per[(minper <= per) & (per <= maxper)]


# Grab a station and look for dead channel days
year = '2015'
sta = 'ANMO'
chan = 'LHZ'
loc = '00'

files = glob.glob('/TEST_ARCHIVE/PSDS/' + sta + '/' + year + '/*' + loc + '_' + chan + '*') 


for idx, curfile  in enumerate(files):
    print 'We are ' + str(float(idx)/float(len(files))*100) + '% done'
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
            print curfile + ' is dead with dB difference ' + str(dbdiff)


        
    
    except:
        print curfile + ' is bad'



