#!/usr/bin/env python
__author__ = 'lpeng'

"""Format conversion: from binary to WTH (DSSAT climate variable)"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. extract point data time series

##============================================================================================

## import library
##---------------
import sys, os, glob, gc, csv
# time handling
import time, calendar
import datetime as dt
from pandas.tseries.offsets import Day
import pandas as pd
from pandas import Series, DataFrame
# tool
import numpy as np
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

wthpath = "/home/water5/lpeng/Projects/CROP/DSSAT45/Weather/old/"
pgfpath = "/home/water5/lpeng/Data/pgf/"
datapath = '/home/water5/lpeng/Projects/CROP/CLIMATE/Weather/'
## import data
##------------
# forcing = ('tas', 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin')
forcing = ('dswrf','tmax', 'tmin', 'prec', 'wind')

# reading point data
site = ("DTCM", "FLSC")
# for st in site:

data = [fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32') for var in forcing]
data = vstack(data).T

# convert unit
data[:, 0] = data[:, 0] / 11.5741		  # SWrad: W/m2 to MJ/m2/day
data[:, 1] = data[: ,1] - 273.16  # Tmax: Kalvin to celcius degree
data[:, 2] = data[: ,2] - 273.16  # Tmin: Kalvin to celcius degree
data[:, 4] = data[: ,4] * 3.6	  # Wind: m/s to km/day
# print data[0][0]


# set up the first date time column
styr = 1948
edyr = 2012
dates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

# generate the raw data
outFile = open("%sRawData.txt" %(datapath), "w")
for i in xrange(0, len(dates)):
	doy = dates[i].strftime("%y%j")
	outFile.write("%d  %.1f  %.1f  %.1f  %.1f  %.1f\n" % (int(doy), data[i, 0], data[i, 1], data[i, 2], data[i, 3], data[i, 4]))
outFile.close()

# try to generate WTH file
# outFile = open("%sTEST.WTH" %(datapath), "w")
# outFile.write("*WEATHER DATA : ABCD\n")
# outFile.write("\n@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT\n")
# outFile.write("  %4s   %.3f   %.3f     %d  %.1f   %.1f   %d   %d\n" %("TEST", 19.010, 99.010, 0, 23.6, 3.7, -99, -99))
# outFile.write("@DATE  SRAD  TMAX  TMIN  RAIN  DEWP  WIND\n")
# for i in xrange(0, len(dates)):
# 	doy = dates[i].strftime("%y%j")
# 	outFile.write("%5s  %2.1f  %2.1f  %2.1f   %2.1f   %2.1f\n" % (doy, data[i, 0], data[i, 1], data[i, 2], data[i, 3], data[i, 4]))
# outFile.close()


# doy = dates.dayofyear
# yr_doy = zip(dates.year, doy)
# time = np.vstack(['%4g%03d' % (m, n) for m, n in yr_doy])
# final = hstack((time, data))
# np.savetxt('%sRawData_nodate.txt' %(datapath), data[:10,:], delimiter="\t", fmt = ['%.1f','%.1f','%.1f','%.1f','%.1f\n'])



# # read template
# header = pd.read_table('%sDTCM6301.WTH' % (wthpath), nrows=3)
# header.to_csv('%sHeader.csv' %(datapath), index = False, sep = '\t', na_rep = " ")
# # combine the date time and the data
# np.savetxt('%sData.csv' %(datapath), final, header = '@DATE  SRAD  TMAX  TMIN  RAIN  WIND', delimiter="  ", fmt = ['%s','%s','%s','%s','%s','%s'])
# # np.savetxt('%sData.csv' %(datapath), final, delimiter="  ", fmt = ['%g','%g','%g','%g','%.1f','%.1f','%.1f','%.1f','%.1f','%.1f','%.1f','%g'])

# remove files
# os.system('cat %sHeader.csv %sData.csv > %sDTCM4801.WTH' %(datapath, datapath, datapath))
# os.system('rm %sHeader.csv' %(datapath))
# os.system('rm %sData.csv' %(datapath))

# write into txt file

