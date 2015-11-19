#!/usr/bin/env python
import glob

import numpy as np

import sys

from obspy.signal.spectral_estimation import get_NLNM
import matplotlib.pyplot as plt

from multiprocessing import Pool

path = '/TEMP_TEST/PSDS/'


# Grab the NLNM and get power and per in the microseism band
minper = 5.
maxper = 10.

per, NLNM = get_NLNM()

micNLNM = NLNM[(minper <= per) & (per <= maxper)]
micper = per[(minper <= per) & (per <= maxper)]



def checkAlive(curfile):
    # Boolean version of dead channel metric    
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
        dbdiff = 1./float(len(NLNMinterp))*sum(stapow-NLNMinterp)
        if dbdiff <= 0.:
            result = False
        else:
            result = True
    except:
        result = False
    return result


def getPercentile(snst):
    year = snst.split('.')[3]
    chan = snst.split('.')[2]
    loc = snst.split('.')[1]
    sta = snst.split('.')[0]
    files = glob.glob(path + sta + '/' + year + '/*' + loc + '_' + chan + '*')
    for idx, curfile in enumerate(files):
        print 'On ' + sta  + ' ' + loc + ' ' + chan + ' ' + year + ' ' + str(100*float(idx)/float(len(files))) + '%' 
        if checkAlive(curfile):
            power = []
            period =[]
            with open(curfile,'r') as f:
                for line in f:
                    power.append(float(line.split(",")[0]))
                    period.append(1./float(line.split(",")[1]))
            if not 'powerArray' in vars():
                powerArray = np.asarray(power)
            else:
                powerArray = np.vstack((powerArray,np.asarray(power)))

    if 'powerArray' in vars():
        # We Now have an array of all the powers and periods  
        (numfiles, length) = powerArray.shape     
        # Grab the 1st, 5th, 25th, and 50th        
        #percentiles = np.empty([4,length])
        fw = open('results/' + sta + loc + chan + year + 'percentile','w')
        fw.write('period, 1st, 5th, 25th, 50th \n')
        for idx in range(0,length):
            fw.write(str(period[idx]) + ', ' + str(np.percentile(powerArray[:,idx],1.)) + ', ' + \
                    str(np.percentile(powerArray[:,idx],5.)) + ', ' + str(np.percentile(powerArray[:,idx],25.)) + \
                    ', ' + str(np.percentile(powerArray[:,idx],50.)) + '\n')
    
    fw.close()    
    return 

if __name__ == "__main__":

    # Used for testing
    #year = '1989'
    #chan = 'LHZ'
    #sta = 'HRV'
    #loc = ''
    #getPercentile(sta + '.' + loc + '.' + chan + '.' + year)

    for year in range(1989,2015):
        stas = glob.glob(path + '*/' + str(year) + '/PSD*')

    goodsncl = []
    for val in stas:
        goodsncl.append(val.split('_')[3] + '.' + val.split('_')[4] + '.' + val.split('_')[5] + '.' + str(year))

    goodsncl = list(set(goodsncl))

    pool = Pool(6)
    pool.map(getPercentile,goodsncl)
    

    









