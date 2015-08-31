__author__ = 'pitch'

"""Counterfactual climate datasets forcing"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. extract point data time series
# 	2. detrend
#   3. add counterfactual trend
##============================================================================================

## import library
##---------------
import sys, os, gc, time
# time handling
import calendar
from pandas import Series, DataFrame
# tool
from netCDF4 import Dataset
from pylab import *
import IO, DataProcess
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
gsdir = '/home/air1/lpeng/Projects/Africa/GrowSeason/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec', 'ETo')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec', 'pet')
units = ('K', 'K', 'W/m2', 'm/s', 'x100%', 'mm/d')

glat = 292
glon = 296
styr = 1979
edyr = 2010
stdy = datetime.datetime(styr, 1, 1)
eddy = datetime.datetime(edyr, 12, 31)
nt = (eddy - stdy).days + 1
nmon = (edyr - styr + 1) * 12

# Define region dimensions
dims = {}
dims['minlat'] = -34.875
dims['minlon'] = -18.875
dims['nlat'] = glat
dims['nlon'] = glon

dims['res'] = 0.250
dims['maxlat'] = dims['minlat'] + dims['res'] * (dims['nlat'] - 1)
dims['maxlon'] = dims['minlon'] + dims['res'] * (dims['nlon'] - 1)
dims['undef'] = -9.99e+08

# Open mask file : this mask is different from Lyndon's mask
# maskdir = '/home/water5/lpeng/Masks/0.25deg/africa/'
# mask_bl = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :].mask
# mask = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :]
# # mask.mask is the boolean values: True and False
mask_bl = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1].mask


## In this section, duplicate codes are written as inner functions
## ========Define inner function =============
def DataStackSave(data_append, freq):

	"""stacking all the data into 3D array"""

	data_append = vstack(data_append)
	if not os.path.exists('%s%s' % (workspace, varname[i])):
		os.makedirs('%s%s' % (workspace, varname[i]))
	data_append.dump('%s%s/%s_%s_%s-%s' %(workspace, varname[i], varname[i], freq, styr, edyr))
	del data_append

	return

def Get_Growseason_Length(pdate, hdate):

	"""compute the length of growing season"""
	scen1 = (pdate >= hdate) * ((365 - pdate) + hdate)
	scen2 = (pdate < hdate) * (hdate - pdate)
	length = scen1 + scen2

	return length

def Get_Area_Trend(data, type, varname):

	"""Inner function for looping Mann-Kendall trend slope"""

	parameters = empty((3, glat, glon))
	parameters.fill(nan)
	for lon in xrange(0, glon):
		print lon
		for lat in xrange(0, glat):
			if mask_bl[lat, lon]:
				continue
			else:
				# parameters[:, lat, lon] = DataProcess.Linear_Trend_Parameter(data[:, lat, lon])
				parameters[:, lat, lon] = DataProcess.MannKendall_Trend_Parameter(data[:, lat, lon])
	# parameters.dump('%s%s/mk_trend_slope_itcpt_%s' % (workspace, varname, type))
	parameters.dump('%s%s/mk_trend_slope_st_ed_%s' % (workspace, varname, type))
	del data, parameters

	return

## ****************************** Main function ******************************
i = 6  # ETo
freq = 'growseason'
step = 3

##=========================================
## Step1: calculate PET using PET FAO56 equation
# This step is finished by Di Tian, which is in the same path

## Step2: aggregate annual growing season time series to calculate MK trend
# (1) merge all the daily data to annual data using CDO
if step == 2.1:
	outdir = '%syearly/' % datadir
	# if not os.path.exists(outdir):
	# 	os.makedirs(outdir)
	# if not os.path.exists('%s%s' % (outdir, var)):
	# 	os.makedirs('%s%s' % (outdir, var))
	[os.system('cdo mergetime %s%s/%s*.nc %s%s/%s.%s.nc' %(datadir, year, forcing[i], outdir, forcing[i], forcing[i], year)) for year in xrange(styr, edyr+1)]

# (2) aggregate annual growing season time series
elif step == 2.2:
	yeardir = '%syearly/' % datadir
	# load growing season calendar data
	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
	## ultimate goal: make a 3D mask that get all the growing season values
	# first step: create masks for two different situation, harvest day is within the same year or next year
	mask_1yr = pdate < hdate  # Boolen values
	mask_2yrs = pdate >= hdate
	# second step: create an end-day array, when the harvest day is within the same year, just make the end day the same as the harvest day; when the harvest day is in the next year, just make the end day as the last day of the year
	edate = hdate * mask_1yr + (-1) * mask_2yrs
	# third step: initialize the 3D mask with length of 366, msmask1 is the mask for this year, gsmask2 is the mask for next year
	gsmask1 = empty((366, glat, glon))
	gsmask1.fill(nan)
	gsmask2 = zeros((366, glat, glon))
	# fourth step: loop for each grid to slice the pdate and edate period and average
	for lat in xrange(0, glat):
		for lon in xrange(0, glon):
			if mask_bl[lat, lon]:
				continue
			else:
				gsmask1[pdate[lat, lon]:edate[lat, lon], lat, lon] = 1
				gsmask2[:hdate[lat, lon], lat, lon] = 1
	gsmask2 = gsmask2 * mask_2yrs; gsmask2[gsmask2==0.0] = nan
	data = []
	for year in xrange(styr, edyr): # since the end of growing season may exceed the last year
		if calendar.isleap(year):
			GSmask1 = gsmask1
		else:
			GSmask1 = gsmask1[:365, :, :]
		if calendar.isleap(year+1):
			GSmask2 = gsmask2
		else:
			GSmask2 = gsmask2[:365, :, :]
		# data = vstack((Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year)).variables[forcing[i]][:] * GSmask1, Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year+1)).variables[forcing[i]][:] * GSmask2))
		# aggregate to annual growing season values
		data.append(nanmean(vstack((Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year)).variables[forcing[i]][:] * GSmask1, Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year+1)).variables[forcing[i]][:] * GSmask2)), axis=0).reshape(1, glat, glon))
		print year
	# convert to 3D annual array
	data = vstack(data)
	data.dump('%spet/pet_%s_%s-%s' %(workspace, freq, styr, edyr))

# (3) calculate MK trend
elif step == 2.3:
	data = load('%s%s/%s_%s_%s-%s' %(workspace, varname[i], varname[i], freq, styr, edyr))
	Get_Area_Trend(data, freq, varname[i])

parameters = load('%s%s/mk_trend_slope_st_ed_%s' % (workspace, varname[i], freq))
plt.imshow(parameters[0, :, :])
plt.show()
exit()
## Step3: detrend the PET according to the two pivots experiments
# y - (slope * x + intercept)
# y - parameters[0, :, :] * x

# if step == 3:
# 	firstyr = datetime.date(styr, 1, 1)
# 	for year in xrange(styr, styr+2):  #edyr):
# 		yrst = datetime.date(year, 1, 1)
# 		yred = datetime.date(year, 12, 31)
# 		nxyr = datetime.date(year+1, 1, 1)
# 		len = (nxyr-yrst).days
# 		print len
# 		x = np.arange(len, dtype=float) + (yrst - firstyr).days
# 		print parameters[0, :, :] * x
		# y = DataProcess.Extract_Data_Period_Average(yrst, yred, None, None, 'open', ctl_out, varname[i], 'all')
		# y - parameters[0, :, :] * x
		# yred = datetime.datetime(year, 12, 31)
		#
	# 		y = np.asarray(y)
	# if y.ndim > 1:
	# 	raise ValueError('y cannot have ndim > 1')
	# if not y.ndim:
	# 	return np.array(0., dtype=y.dtype)
	#
	# 	print ().days
		#

exit()

# make a growing season mask
## Step4: resample from the PET
# ensemble = np.empty((len(forcing)-1, 365, 10))  # delta
# day = datetime.date(styr, 1, 1)
# for lon in xrange(0, glon):
# 	for lat in xrange(0, glat):
# 		if mask_bl[lat, lon]:
# 			continue
# 		else:
# 			data_append = []
#
# 			for year in xrange(styr, edyr): # since the end of growing season may exceed the last year
# 				stdy = datetime.datetime.strptime(str(year)+str(int(round(pdate[lat, lon]))), '%Y%j')
# 				gsyr = (pdate[lat, lon] >= hdate[lat, lon]) * (year+1) + (pdate[lat, lon] < hdate[lat, lon]) * year   # This condition argument is good for numbers only
# 				eddy = datetime.datetime.strptime(str(gsyr)+str(int(round(hdate[lat, lon]))), '%Y%j')
# 				data_append.append(DataProcess.Extract_Data_Period_Average(stdy, eddy, lat, lon, 'open', ctl_out, varname[i], type))
# 			data_append = vstack(data_append).reshape(-1)
# 			parameters[:, lat, lon] = DataProcess.MannKendall_Trend_Parameter(data_append)
# 			print lat, lon



# for d in xrange(0, 365):  # delta):
# 	curdy = stdy + dt.timedelta(d)
# 	# For each single day, sample an ensemble with a 7-day window across multiple years
# 	pool = Series()  # initialize a Series-type variable
# 	if curdy.day == 29 and curdy.month == 2:
# 		for year in xrange(styr+1, styr+10): #edyr+1):
# 			if calendar.isleap(year):
# 				print year
# 				curdy_year = dt.datetime(year, curdy.month, curdy.day)
# 				pool = pool.append(ts[curdy_year-3*Day(): curdy_year+3*Day()])
# 	else:
# 		for year in xrange(styr+1, styr+10): #edyr+1):
# 			curdy_year = dt.datetime(year, curdy.month, curdy.day)
# 			pool = pool.append(ts[curdy_year-3*Day(): curdy_year+3*Day()])
#
# 	# Pick up the first 10 days with closest values
# 	dif = abs(pool - ts[curdy])
# 	# sort by values
# 	collect = dif.order()
# 	# constraint
# 	dy_collect = collect[:10].index
#
# 	for j in xrange(0, len(forcing)-1):
# 		# for i in xrange(0, 10):
# 		# 	day = dy_collect[i]
# 		# print dy_collect
# 		# print data[j][dy_collect]
# 		# print year, curdy.month, curdy.day
# 		ensemble[j,d,:] = data[j][dy_collect]
#
# # print ensemble[2,:,:]
#
#
# 		timeseries_update = data_detrend + ave
# 			del timeseries_update, timeseries, data_detrend





## Calculate trend of all climate variables
##=========================================
## Step1: Aggregate time series to calculate mann kendall trend
flag = 0
if flag == 1:
	freq = 'annual'
	types = ('ave', 'ave', 'ave', 'ave', 'ave', 'pre') # aggregating method
	for i in xrange(0, len(forcing)):
		ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], 1948, edyr)

		## monthly time series to calculate linear trend
		if freq == 'monthly':
			# initial month start day
			monst = stdy
			data_append = []
			for j in xrange(0, nmon):
				# end day of the month
				moned = monst + relativedelta(months=1) - relativedelta(days=1)
				data = DataProcess.Extract_Data_Period_Average(monst, moned, None, None, 'open', ctl_out, varname[i], types[i])
				# Convert 2-d arrays to 3-d for stacking
				data_append.append(data.reshape(1, glat, glon))
				del data
				print monst, moned
				# Update month starting date
				monst = monst + relativedelta(months=1)

			DataStackSave(data_append, freq)

		## annual time series to calculate linear trend
		elif freq == 'annual':
			data_append = []
			for year in xrange(styr, edyr+1):
				yrst = datetime.datetime(year, 1, 1)
				yred = datetime.datetime(year, 12, 31)
				data = DataProcess.Extract_Data_Period_Average(yrst, yred, None, None, 'open', ctl_out, varname[i], types[i])
				# Convert 2-d arrays to 3-d for stacking
				data_append.append(data.reshape(1, glat, glon))
				del data
				print yrst, yred

			DataStackSave(data_append, freq)

## Step2: Get parameters from regression based on theil's slope (Mann kendall)
if flag == 2:
	for i in xrange(0, len(forcing)):
		Get_Area_Trend('annual', varname[i])

exit()

