#!/usr/bin/env python3

import os, argparse
from datetime import datetime, timedelta
import glob
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#===============================================================================
# Data
#
dbdir  = '/var/services/homes/jacopo/repos/raumklima/database'
figdir = '/var/services/web/web_images/'
nsensors = 7
snames = [
        'Kitchen',
        'Livingrm',
        'Studio',
        'Bedrm',
        'Bathrm',
        'East',
        'West',
        ]
limsT  = [18, 27]
limsRH = [40, 70]
colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

#===============================================================================
# Classes
#
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
        self.s6 = sensors[5]
        self.s7 = sensors[6]

#===============================================================================
# Functions
#
#-------------------------------------------------------------------------------
def readDB(fpath):

    # read database
    ifile = open(fpath, 'r')
    csvreader = csv.reader(ifile)
    rows = []
    for row in csvreader:
        rows.append(row)
    ifile.close()

    # convert data
    Tnsensors = len(rows[0])-1
    if Tnsensors != nsensors:
        raise ValueError('Number of sensors in table ({}) != from module nsensors ({}).'.format(Tnsensors, nsensors))
    #
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

    return table

#-------------------------------------------------------------------------------
def doPlotly(table, nback=0, figName='fig.html'):


    nback = -min(table.shape[0], -nback)

    fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("Temperature", "Relative Humidity"),
            shared_xaxes=True,
            vertical_spacing=0.04,
            )

    for s in range(nsensors):
        label = snames[s]
        fig.add_trace(go.Scatter(x=table[nback:, 0], y=table[nback:, 1+2*s  ], name=label,         mode='lines', line=dict(color=colors[s], width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=table[nback:, 0], y=table[nback:, 1+2*s+1], name=label.lower(), mode='lines', line=dict(color=colors[s], width=2)), row=2, col=1)

    for trace in fig['data']: 
        if(trace['name'].islower()): trace['showlegend'] = False
    fig.update_layout(
            height=800, width=700,
            title_text="",
            hovermode = 'x unified'
            )
    fig.write_html(os.path.join(figdir, figName))

#-------------------------------------------------------------------------------
def doMatplotlib(table, nback=0, figName='fig.png'):

    nback = -min(table.shape[0], -nback)

    fig = plt.figure(1); fig.clear()
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True, num=fig.number)
    limsT  = [1e6, -1e6]
    limsRH = [1e6, -1e6]
    for s in range(nsensors):
        if figName[0:3] != 'avg':
            label = '{0:.1f} '.format(table[-1,1+2*s]) + snames[s]
        else:
            label = snames[s]
        ax[0].plot(table[nback:, 0], table[nback:, 1+2*s])
        ax[1].plot(table[nback:, 0], table[nback:, 1+2*s+1], label=label)
        #
        if s <= 4:
            limsT [0] = min(limsT [0], np.min(table[nback:, 1+2*s]))
            limsT [1] = max(limsT [1], np.max(table[nback:, 1+2*s]))
            limsRH[0] = min(limsRH[0], np.min(table[nback:, 1+2*s+1]))
            limsRH[1] = max(limsRH[1], np.max(table[nback:, 1+2*s+1]))
    limsT  = [limsT [0]-0.5, limsT [1]+0.5]
    limsRH = [limsRH[0]-2.0, limsRH[1]+2.0]

    ax[1].xaxis.set_major_formatter(
                mdates.ConciseDateFormatter(ax[1].xaxis.get_major_locator()))
    # Shrink current axis's height by 10% on the bottom
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0 + box.height * 0.1,
                         box.width, box.height * 0.9])
    # Put a legend below current axis
    ax[1].legend(loc='upper center', bbox_to_anchor=(0.40, -0.10),
                      fancybox=True, shadow=False, ncol=4, fontsize='small')
    ax[0].set_ylim(limsT)
    ax[1].set_ylim(limsRH)
    #ax[1].set_xlim([table[max(nback, -table.shape[0]),0], table[-1,0]])
    ax[1].set_xlim([(table[-1,0]-timedelta(days=1)), table[-1,0]])
    ax[0].set_ylabel('Temp')
    ax[1].set_ylabel('RH')
    #ax[1].set_xlabel('Time')
    ax[0].grid(visible=True, which='major', axis='y', alpha=0.3)
    ax[1].grid(visible=True, which='major', axis='y', alpha=0.3)
    plt.draw()
    plt.savefig(os.path.join(figdir, figName), dpi=300, bbox_inches='tight')
    #pickle.dump(fig, open(figdir + '24hrs.fig.pickle', 'wb'))
    #print('saved 24hrs')

#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
#plt.gca().xaxis.set_major_locator(mdates.DayLocator())
#plt.plot(x,y)
#plt.gcf().autofmt_xdate()

#-------------------------------------------------------------------------------
def doAvgMatplotlib(fpath, ndays=1):

    # get files
    dbFiles = glob.glob(fpath+'*.csv')
    dbFiles.sort()

    # process averages
    avgTable   = np.zeros(2*nsensors+1)
    runningAvg = np.zeros(2*nsensors)
    day = None
    ntsteps = 0
    for week in dbFiles:
        table = readDB(week)
        for i in range(table.shape[0]):
            if (day == None) or ((table[i,0].date() - day).days >= ndays):
                # initialise / reset start day
                day = table[i,0].date()
                if ntsteps > 0:
                    # save running average
                    avgTable = np.vstack( (avgTable,  np.append(np.array([day]), runningAvg/ntsteps)) )
                    runningAvg = np.zeros(2*nsensors)
                    ntsteps = 0
            else:
                # add current time stamp to average
                runningAvg += table[i, 1:].astype(float)
                ntsteps += 1
    avgTable = np.delete(avgTable, (0), axis=0)
    doMatplotlib(avgTable, nback=0, figName='avg_{0:02d}days.png'.format(ndays))

#-------------------------------------------------------------------------------
def read_and_plot(plotKind='avg'):

    now  = datetime.now()
    year = now.year
    wnum = now.isocalendar()[1]

    yearPath = os.path.join(dbdir, '{:4d}'.format(year))

    if plotKind == '24hrs':
        fname = 'w{:02d}.csv'.format(wnum)
        table = readDB(os.path.join(yearPath,fname))
        doMatplotlib(table, nback=-24*60, figName='24hrs.png')
        doPlotly    (table, nback=-24*60, figName='24hrs.html')
    elif plotKind == 'avg':
        doAvgMatplotlib(yearPath, ndays=1)


#===============================================================================
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = "Make plots.")
    parser.add_argument('-k', '--kind', type=str, default='24hrs', help="what plots")
    args = parser.parse_args()

    read_and_plot(plotKind=args.kind)
