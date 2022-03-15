#!/usr/bin/env python3

from datetime import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def Sensor():
    def __init__(self, T=0, RH=0):
        self.t  = T
        self.rh = RH

def Data():

    def __init__(self, tstamp=None, sensors=[]):
        self.tstamp  = tstamp
        self.sensors = sensors
        #
        self.s1 = sensors[0]
        self.s2 = sensors[1]
        self.s3 = sensors[2]
        self.s4 = sensors[3]
        self.s5 = sensors[4]

snames = [
        'Sala',
        'Studio',
        'Camera',
        'Bagno',
        'Cucina'
        ]

def readDB(fpath):

    # read database
    ifile = open(fpath, 'r')
    csvreader = csv.reader(ifile)
    rows = []
    for row in csvreader:
        rows.append(row)
    ifile.close()

    # convert data
    nsensors = len(rows[0])-1
    table = np.zeros(2*nsensors+1)
    for row in rows:
        tstamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
        sensors = np.zeros(2*nsensors)
        for s in range(nsensors):
            T  = float(row[1+s][0:6])
            RH = float(row[1+s][7:])
            sensors[2*s:2*s+2] = [T, RH]
        table = np.vstack( (table,  np.append(np.array([tstamp]), sensors)) )

    table = np.delete(table, (0), axis=0)

    return table, nsensors

def do24hrsPlot(dbdir, fpath):

    table, nsensors = readDB(fpath)

    # Plot last 24 hrs
    nback = 24*60
    fig = plt.figure(1); fig.clear()
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, num=fig.number)
    for s in range(nsensors):
        ax[0].plot(table[-nback:, 0], table[-nback:, 1+2*s]  )
        ax[1].plot(table[-nback:, 0], table[-nback:, 1+2*s+1], label=snames[s])
    ax[1].xaxis.set_major_formatter(
                mdates.ConciseDateFormatter(ax[1].xaxis.get_major_locator()))
    # Shrink current axis's height by 10% on the bottom
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])
    # Put a legend below current axis
    ax[1].legend(loc='upper center', bbox_to_anchor=(0.40, -0.10),
                      fancybox=True, shadow=False, ncol=5, fontsize='small')
    ax[0].set_ylabel('Temp')
    ax[1].set_ylabel('RH')
    #ax[1].set_xlabel('Time')
    ax[1].set_xlim([table[max(-nback, -table.shape[0]),0], table[-1,0]])
    ax[1].set_ylim([30, 55])
    ax[0].grid(visible=True, which='major', axis='y', alpha=0.3)
    ax[1].grid(visible=True, which='major', axis='y', alpha=0.3)
    plt.draw()
    plt.savefig(dbdir + '24hrs.png', dpi=300, bbox_inches='tight')
    #pickle.dump(fig, open(dbdir + '24hrs.fig.pickle', 'wb'))
    #print('saved 24hrs')

def doAvgPlot(dbdir, fpath):

def read_and_plot(plotKind='24hr'):

    dbdir  = '/home/pi/repos/raumklima/database/'

    now  = datetime.now()
    year = now.year
    wnum = now.isocalendar()[1]

    if plotKind == '24hrs':
        fpath = dbdir + '{:4d}/'.format(year)
        fname = 'w{:02d}.csv'.format(wnum)
        do24hrsPlot(dbdir, fpath + fname)
    elif plotKind == 'avg':
        doAvgPlot(dbdir, fpath)


if __name__ == '__main__':
    read_and_plot()
