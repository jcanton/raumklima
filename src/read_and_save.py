#!/usr/bin/env python3

from rs500reader.reader import Rs500Reader
from datetime import datetime
import time, os

nsensors = 7
maxTries = 20
#             1     2      3      4      5      6      7
offsetsT  = [ 0.0,  0.37, -0.12,  0.02,  0.25,  0.05,  0.08]
offsetsRH = [ 0,    0,     0,     0,     0,     0,     0   ]  

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
        for i in range(1, 9, 1):
            chan_data = data.get_channel_data(i)
            if chan_data is not None:
                cd.append( chan_data )

    if len(cd) == nsensors:
        ofile = open(fpath + fname, 'a')
        ofile.write(tstamp)
        for i in range(len(cd)):
            ofile.write(', {:4.1f} | {:2d}'.format(cd[i].temperature + offsetsT[i], cd[i].humidity + offsetsRH[i]))
    
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
    get_and_save()
