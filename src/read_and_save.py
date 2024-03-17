#!/usr/bin/env python3

from rs500reader.reader import Rs500Reader
from datetime import datetime
import time, os

nsensors = 7
maxTries = 50
#             1     2      3      4      5      6      7
offsetsT  = [ 0.0,  0.37, -0.12,  0.02,  0.25,  0.05,  0.08]
offsetsRH = [ 0,    0,     0,     0,     0,     0,     0   ]

class Dummy:
    def __init__(self, T, H):
        self.temperature=T
        self.humidity=H

def get_and_save():

    reader = Rs500Reader()
    dbdir  = '/home/pi/repos/raumklima/database/'

    now  = datetime.now()
    tstamp = now.strftime('%Y-%m-%d %H:%M:%S')

    year = now.year
    wnum = now.isocalendar()[1]

    fpath = dbdir + '{:4d}/'.format(year)
    fname = 'w{:02d}.csv'.format(wnum)

    if not os.path.isdir(fpath):
        os.makedirs(fpath)

    cd = []
    tryNr = 0
    while (len(cd) != nsensors) and (tryNr < maxTries):
        data = reader.get_data()
        cd = []
        tryNr += 1
        for i in range(1, nsensors+1, 1):
            chan_data = data.get_channel_data(i)
            if chan_data is not None:
                cd.append( chan_data )
        #time.sleep(1)

    print('Received data from {0:d}/{1:d} sensors in {2:d} tries'.format(len(cd), nsensors, tryNr))
    if tryNr == maxTries:
        cd = []
        cds = "["
        for i in range(1, nsensors+1, 1):
            chan_data = data.get_channel_data(i)
            if chan_data is not None:
                cd.append( chan_data )
                cds += '{0:d}: Y, '.format(i)
            else:
                cd.append( Dummy(T=float("NaN"), H=float("NaN")) )
                cds += '{0:d}: N, '.format(i)
        cds += "]"
        print('\tCould not get all sensors: ' + cds)
        print('\t[' + ', '.join(['{0:.1f}'.format(cd[i].temperature) for i in range(nsensors)]) + ']')


    if len(cd) == nsensors:
        ofile = open(fpath + fname, 'a')
        ofile.write(tstamp)
        for i in range(len(cd)):
            ofile.write(', {:4.1f} | {:2.1f}'.format(cd[i].temperature + offsetsT[i], float(cd[i].humidity + offsetsRH[i])))
    
        ofile.write('\n')
        ofile.close()

def get_and_save_repeat():

    reader = Rs500Reader()
    dbdir  = '/home/pi/repos/raumklima/database/'
    interval = 60 # seconds

    while True:

        data = reader.get_data()
        now  = datetime.now()
        tstamp = now.strftime('%Y-%m-%d %H:%M:%S')

        year = now.year
        wnum = now.isocalendar()[1]

        fpath = dbdir + '{:4d}/'.format(year)
        fname = 'w{:02d}.csv'.format(wnum)

        if not os.path.isdir(fpath):
            os.makedirs(fpath)

        ofile = open(fpath + fname, 'a')
        ofile.write(tstamp)

        for i in range(1, 9, 1):
            chan_data = data.get_channel_data(i)
            if chan_data is not None:
                ofile.write(', {:4.1f} | {:2d}'.format(chan_data.temperature, chan_data.humidity))

        ofile.write('\n')
        ofile.close()

        time.sleep(interval)


if __name__ == '__main__':
    print('\n\nStarting at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    get_and_save()
    print('Finished at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
