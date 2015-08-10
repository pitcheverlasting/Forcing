#!/usr/bin/env python
__author__ = 'lpeng'

"""PE P percentage change"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. extract point data time series
##============================================================================================

import FORCING, WEATHER
from pylab import *
import time, calendar
import numpy as np
import datetime as dt
from pandas.tseries.offsets import Day
import pandas as pd
from pandas import Series
## import data
##------------
# data path
datapath = '/home/water5/lpeng/Projects/CROP/CLIMATE/Weather/'
pgfpath = '/home/water5/lpeng/Data/pgf/'
forcing = ('tas', 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin')
site = ("DTCM", "FLSC")

# Simulating years 1961-2010
styr = 1981
edyr = 1982
Sdates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

## To sample across the sampling years, I use the original longer time series 1948-2012, which is not necessary but convinient
Fdates = pd.date_range((str(1948)+'-01-01'), (str(2012)+'-12-31'), freq='D')
## reading data as full time series # For Sampling
Fdata = [Series(fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32'), index=Fdates) for var in forcing]

## Calculate the start day of 1961-01-01 relative to 1948-01-01, so that I can extract from the full time series
stdate = pd.date_range((str(1948)+'-01-01'), (str(styr-1)+'-12-31'), freq='D')
eddate = pd.date_range((str(1948)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

## Calculate weather data, most important, PE_fao
# This is just for the FORCING package reference
Fdata_mat = [fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32') for var in forcing]
Fdata_mat = vstack(Fdata_mat).T
climate = FORCING.Data(Fdata_mat)
Sdata_mat = [fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32')[len(stdate):len(eddate)] for var in forcing]
Sdata_mat = vstack(Sdata_mat).T
Sclimate = FORCING.Data(Sdata_mat)
del Sdata_mat

# write files test
# weather = [Sclimate.SWin, Sclimate.Tmax, Sclimate.Tmin, Sclimate.Prec, Sclimate.Td, Sclimate.Wind]
# weather = vstack(weather).T
# WEATHER.File(weather, dir=datapath, sy=styr, ey=edyr, filename=("AA%02d%02d" %(1,1)))
# exit()

## Looking for PE across multiple years that close to climate_ave.PE_fao and its changes
# pe from 1948-2012
Fpe = Series(climate.PE_fao, index=Fdates)
# pe for 50 years
Spe = Series(Sclimate.PE_fao, index=Sdates)



## Start sampling
nt = len(Sdates)
ns = 10

## Percentage change
## Modify parameter : factor here
factor = [(0.7 + i/100.0) for i in xrange(0, 61, 2)]
# Precipitation
p_ensemble = [Sclimate.Prec * factor[i] for i in xrange(0, len(factor))]
# Potential Evapotranspiration
pe_ensemble = [Spe * factor[i] for i in xrange(0, len(factor))]


## Create a empty array for all the forcings, 366 days, 10 ensemble members
ensemble = np.empty((len(factor), len(forcing), nt, ns))

## Loop for each single day in the time series
for d in xrange(0, nt):
	# get the current date timestamp curdy given the looping number d
	curdy = dt.datetime(styr, 1, 1) + dt.timedelta(d)
	# For each single day, sample an ensemble with a 7-day window across multiple years
	pool = Series()  # initialize a Series-type variable
	# for 2,29 skip nonleap years
	if curdy.day == 29 and curdy.month == 2:
		for year in xrange(1949, 2012): # 1961-2010
			if calendar.isleap(year):
				print year
				curdy_year = dt.datetime(year, curdy.month, curdy.day)
				pool = pool.append(Fpe[curdy_year-7*Day(): curdy_year+7*Day()])
	else:
		for year in xrange(1949, 2012):
			curdy_year = dt.datetime(year, curdy.month, curdy.day)
			pool = pool.append(Fpe[curdy_year-7*Day(): curdy_year+7*Day()])

	# Compare samping values
	# i: the percentage
	for i in xrange(0, len(factor)):
		# difference the sampling pool with the current value
		dif = abs(pool - pe_ensemble[i][curdy])
		# sort by values
		collect = dif.order()
		# Pick up the first ns=10 days with closest values
		dy_collect = collect[0:ns].index
		# Assign the forcings sets on the selected days
		for m in xrange(0, len(forcing)):
			ensemble[i, m, d, :] = Fdata[m][dy_collect]

		## CONSTRAINT on the ns ensemble members
		CR = 0.15   # non closure rate: which means the 85% threshold
		for n in xrange(0, ns):
			# within threshold: dif < 15%, don't change ensemble assignment in the previous command
			# above threshold: dif > 15%, recalculate Tmax, or Tmin to replace the old value using Penman FAO56 scheme
			if collect[n:n+1].item() > CR * pe_ensemble[i][curdy]:
				# get the index of selected value
				delta = pd.to_datetime(dy_collect[n]) - dt.datetime(1948,1,1)
				# Use FORCING library to calculate Tmax, transform into kelvin
				Tmax_analytical = FORCING.Data(Fdata_mat).Calculate_Tmax((factor[i]), delta.days) + 273.16
				if Tmax_analytical > ensemble[i, 8, d, n]:
					ensemble[i, 7, d, n] = Tmax_analytical
				else:
					Tmin_analytical = FORCING.Data(Fdata_mat).Calculate_Tmin((factor[i]), delta.days) + 273.16
					# print ensemble[i, 7, d, n], Tmax_analytical, ensemble[i, 8, d, n], Tmin_analytical
					if Tmin_analytical < ensemble[i, 7, d, n]:
						ensemble[i, 8, d, n] = Tmin_analytical
					else:
						k = np.random.randit(ns, size=2)
						ensemble[i, 7, d, n] = ensemble[i, 7, d-1, k[0]]
						ensemble[i, 8, d, n] = ensemble[i, 8, d-1, k[1]]

del Fpe
del Spe
# Year = np.arange(0, 365)
# fig,([ax1,ax2],[ax3,ax4]) = plt.subplots(2,2,sharex=True,sharey=False)
# fig.suptitle("Sampled Weather Data with PE $\pm$ 30%", fontsize=22)
#
# L = [FORCING.Data(mean(ensemble[i,:,:,:],axis=2).T).Tmax for i in xrange(0, len(factor))]
# ax1.plot(L[0],'--r')
# ax1.plot(L[len(factor)-1],'--r')
# ax1.plot(Sclimate.Tmax[0:365],'-ok',linewidth=1.5)
# ax1.fill_between(Year,L[0], L[len(factor)-1], facecolor='r',alpha = 0.3)
# ax1.set_xlim([-1,len(Year)])
# ax1.set_xticks(Year[::90])
# ax1.set_xlabel("Day of Year",fontsize=18)
# ax1.set_title("Tmax",fontsize=20)
# del L
# L = [FORCING.Data(mean(ensemble[i,:,:,:],axis=2).T).Tmin for i in xrange(0, len(factor))]
# ax2.plot(L[0],'--b')
# ax2.plot(L[len(factor)-1],'--b')
# ax2.plot(Sclimate.Tmin[0:365],'-ok',linewidth=1.5)
# ax2.fill_between(Year,L[0], L[len(factor)-1], facecolor='b',alpha = 0.3)
# ax2.set_xlim([-1,len(Year)])
# ax2.set_xticks(Year[::90])
# ax2.set_xlabel("Day of Year",fontsize=18)
# ax2.set_title("Tmin",fontsize=20)
# del L
# L = [FORCING.Data(mean(ensemble[i,:,:,:],axis=2).T).SWin for i in xrange(0, len(factor))]
# ax3.plot(L[0],'--y')
# ax3.plot(L[len(factor)-1],'--y')
# ax3.plot(Sclimate.SWin[0:365],'-ok',linewidth=1.5)
# ax3.fill_between(Year,L[0], L[len(factor)-1], facecolor='y',alpha = 0.3)
# ax3.set_xlim([-1,len(Year)])
# ax3.set_xticks(Year[::90])
# ax3.set_xlabel("Day of Year",fontsize=18)
# ax3.set_title("SRad",fontsize=20)
# del L
# L = [FORCING.Data(mean(ensemble[i,:,:,:],axis=2).T).Wind for i in xrange(0, len(factor))]
# ax4.plot(L[0],'--g')
# ax4.plot(L[len(factor)-1],'--g')
# ax4.plot(Sclimate.Wind[0:365],'-ok',linewidth=1.5)
# ax4.fill_between(Year,L[0], L[len(factor)-1], facecolor='g',alpha = 0.3)
# ax4.set_xlim([-1,len(Year)])
# ax4.set_xticks(Year[::90])
# ax4.set_xlabel("Day of Year",fontsize=18)
# ax4.set_title("Wind",fontsize=20)

# plt.show()


for i in xrange(0, len(factor)):
	ens_mean = mean(ensemble[i, :, :, :], axis=2).T
	sample = FORCING.Data(ens_mean)
	for j in xrange(0, len(factor)):
		weather = [sample.SWin, sample.Tmax, sample.Tmin, p_ensemble[j][0:nt], sample.Td, sample.Wind]
		weather = vstack(weather).T
		WEATHER.File(weather, dir=datapath, sy=styr, ey=edyr, filename=("%02d%02d" %(i,j)))

exit()
# plt.figure()
# plt.plot(sample.PE_fao)
# plt.plot(climate_ave.PE_fao)
Year = np.arange(styr, edyr)
plt.xlim([-1,len(Year)])
plt.xticks(range(len(Year))[::5],Year[::5],fontsize=15)
plt.xlabel('Year',fontsize=20)
plt.show()
exit()
# prepare forcing

# site = ("DTCM", "FLSC")
# data = [fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32')[len(stdate):len(eddate)] for var in forcing]
# data = vstack(data).T
# climate = FORCING.Data(data)


"""
# Just for the averaging time series
## Calculate the mean value of 366 days
## Beware of the leap year, using month and day
Sdata_ave = [Sdata[i].groupby([Sdata[i].index.month, Sdata[i].index.day]).mean()  for i in xrange(len(forcing))]
Sdata_ave = np.vstack(Sdata_ave).T

# Maintain the rainfall structure
climate_ave = FORCING.Data(Sdata_ave)
test = [Sdata[6][dt.datetime(yr,1,1):dt.datetime(yr,12,31)] for yr in xrange(1964,2011,4)]
structure = []
for yr in xrange(1964,2011,4):
	temp = Sdata[6][dt.datetime(yr,1,1):dt.datetime(yr,12,31)]
	temp[temp>0] = 1
	structure.(temp)

p_ave = [climate_ave.Prec * (vstack(structure[k]).T) for k in xrange(0, 12)]

# pe averaging across multiple years
doy = pd.date_range((str(1976)+'-01-01'), (str(1976)+'-12-31'), freq='D')
pe_ave = Series(climate_ave.PE_fao, index=doy)

for i in range(12):
	plt.plot(climate_ave.Prec,label="Mean")
	plt.plot(p_ave[10].T,label="2004 sample")
	st = pd.date_range((str(1948)+'-01-01'), (str(2003)+'-12-31'), freq='D')
	ed = pd.date_range((str(1948)+'-01-01'), (str(2004)+'-12-31'), freq='D')
	# plt.plot(climate.Prec[len(st):len(ed)],label="2004 observation")
	# plt.legend("averaging",,)

	# plt.plot(climate_ave.PE_fao)
	# plt.plot(climate_ave.Tmax)
	# plt.plot(climate_ave.Tmin)
	# plt.plot(climate_ave.Prec)
	# plt.show()
	# exit()

"""

# write data
for i in xrange(20, 21):
	pc = (1.0+i/100.0)
	weather = [climate.SWin, climate.Tmax, climate.Tmin, climate.Prec * pc, climate.Td, climate.Wind]
	# weather = vstack(weather).T
	# WEATHER.File(weather, dir=datapath, sy=styr, ey=edyr, filename=("PP%02d" %(i)))
	del weather
	# nc = (1.0-i/100.0)
	# weather = [climate.SWin, climate.Tmax, climate.Tmin, climate.Prec * nc, climate.Td, climate.Wind]
	# weather = vstack(weather).T
	# WEATHER.File(weather, dir=datapath, sy=styr, ey=edyr, filename=("PP%02d" %(i)))
plt.plot(climate.Prec*1.2)
plt.plot(climate.Prec)
plt.show()
exit()



	# Test using figure
#
# plt.xlim([-1,len(Year)])
# plt.xticks(range(len(Year))[::5],Year[::5],fontsize=15)
# plt.xlabel('Year',fontsize=20)
# plt.xticks(range(len(Year))[::5],Year[::5],fontsize=15)
# plt.xlabel('Year',fontsize=20)
# plt.show()
#
# exit()


## reading data as simulating time series
# Sdata = [Series(fromfile('%s%s_%s_1948-2012_point.bin' % (pgfpath, site[0], var),'float32')[len(stdate):len(eddate)], index=Sdates) for var in forcing]
# test for the annual value of simulating period
# Sdata_ann = [Sdata[i].groupby([Sdata[i].index.year]).sum()  for i in xrange(len(forcing))]
# plt.plot(Sdata_ann[6],'--og')
# plt.plot(climate.Prec*1.10)


	# prepare forcing
	# test=ensemble[:,:,0]
	# test1 = FORCING.Data(test)
	# ens = [FORCING.Data(ensemble[:,:,i]) for i in xrange(0,)]

