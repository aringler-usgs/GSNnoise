#!/usr/bin/env python

import glob

from obspy.core import read, Stream, UTCDateTime
from matplotlib.mlab import csd
from obspy.signal.invsim import evalresp
import numpy as np
import matplotlib.pyplot as plt
from obspy.signal.spectral_estimation import get_NLNM
from obspy.iris import Client
from multiprocessing import Pool

import os
import sys

client = Client()

def getspectra(string):
    try:
    #if True:
        debug = True
        lenfft = 20000
        resppath = '/APPS/metadata/RESPS/'
        stringTEMP = string.split('_')
                
        net = stringTEMP[0]
        sta = stringTEMP[1]
        loc = stringTEMP[2]
        chan = stringTEMP[3]
        year = stringTEMP[4]
        jday = stringTEMP[5]
        if debug:
            print 'Working on: ' + net + ' ' + sta + ' ' + loc + ' ' + chan
    
        stime = UTCDateTime(year + '-' + jday + "T00:00:00")
        st = client.timeseries(net, sta, loc, chan, stime, stime + 24*60*60)
        if debug:
            print(st)
        if len(st) == 1:
            power,freq = csd(st[0].data,st[0].data, NFFT = lenfft, 
                            noverlap = int(lenfft*.5), Fs = 1/st[0].stats.delta, 
                            scale_by_freq = True)
            power = power[1:].real
            freq = freq[1:]
            
            resp = evalresp(t_samp = st[0].stats.delta, nfft = lenfft, filename= resppath + 'RESP.' + net + '.' + \
                            sta + '.' + loc + '.' + chan,  date = st[0].stats.starttime, station = sta,
                            channel = chan, network = net, locid = loc, units = 'ACC') 
            resp = resp[1:]

            power = 10.*np.log10(power/np.absolute(resp*np.conjugate(resp)))   
        else:
            power =[]
            freq=[]
        if len(power) > 1:
            if debug:
                print 'Writing data for: ' + string
            if not os.path.exists('/TEST_ARCHIVE/PSDS/' + sta):
                os.makedirs('/TEST_ARCHIVE/PSDS/' + sta)
            if not os.path.exists('/TEST_ARCHIVE/PSDS/' + sta + '/' + year):
                os.makedirs('/TEST_ARCHIVE/PSDS/' + sta + '/' + year)
            fpsd = open('/TEST_ARCHIVE/PSDS/' + sta + '/' + year + '/PSD_' + string,'w')
            for p,f in zip(power,freq):
                fpsd.write(str(p) + ', ' + str(f) + '\n')
            fpsd.close() 
    except:
        print 'Unable to process: ' + string  
    return



if __name__ == "__main__":
    debug = True
    network = 'II'
    for year in range(1989,2015):
        year = str(year)
        for jday in range(246,367):
            strings = []
            jday = str(jday).zfill(3)
            mdgetOUTPUT = os.popen('mdget -b ' + year + ',' + jday + '-00:00:00 -s \'' + network + '.....[BL]H...\'')
            for line in mdgetOUTPUT:
                if '* NETWORK' in line:
                    net = (line.replace('* NETWORK','')).strip()
                    tempString = net + '_'
                if '* STATION' in line:
                    sta = (line.replace('* STATION','')).strip()
                    tempString += sta + '_'
                if '* COMPONENT' in line:
                    comp = (line.replace('* COMPONENT','')).strip()
                if '* LOCATION' in line:
                    loc = (line.replace('* LOCATION','')).strip()
                    tempString += loc + '_' + comp + '_' + year + '_' + jday
                    if not os.path.isfile('/TEST_ARCHIVE/PSDS/' + sta + '/' + year + '/PSD_' + net + \
                            '_' + sta + '_' + loc + '_' + comp + '_' + year + '_' + jday):
                        print 'Adding: ' + tempString
                        strings.append(tempString)

            if debug:
                print 'Here are the number of strings: ' + str(len(strings))
                print 'Here is the day: ' + str(jday) + ' ' + str(year)
            #for string in strings:
            pool = Pool(14)
            pool.map(getspectra,strings)            
            #getspectra(strings[1])
