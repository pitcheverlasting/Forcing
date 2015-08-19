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
import sys, os, gc
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
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec')
units = ('K', 'K', 'W/m2', 'm/s', 'x100%', 'mm/d')

glat = 292
glon = 296
styr = 1948
edyr = 2010
stdy = datetime.datetime(styr, 1, 1)
eddy = datetime.datetime(edyr, 12, 31)
nt = (eddy - stdy).days + 1
nmon = (edyr - styr + 1) * 12

# Define region dimensions
dims = {}
dims['minlat'] = -34.875
dims['minlon'] = -18.875
dims['nlat'] = 292
dims['nlon'] = 296

dims['res'] = 0.250
dims['maxlat'] = dims['minlat'] + dims['res'] * (dims['nlat'] - 1)
dims['maxlon'] = dims['minlon'] + dims['res'] * (dims['nlon'] - 1)
dims['undef'] = -9.99e+08

# Open mask file
maskdir = '/home/water5/lpeng/Masks/0.25deg/africa/'
# mask.mask is the boolean values: True and False
mask = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :].mask

## ========Define inner function =============
def Get_Area_Trend(type, varname):

	"""Inner function for looping Mann-Kendall trend slope"""

	if type == 'monthly':
		data = load('%s%s/%s_monthly_%s-%s' %(workspace, varname, varname, styr, edyr))
	elif type == 'annual':
		data = load('%s%s/%s_annual_%s-%s' %(workspace, varname, varname, styr, edyr))
	print "%s loaded" % varname
	parameters = empty((2, glat, glon))
	parameters.fill(nan)
	for lon in xrange(0, glon):
		for lat in xrange(0, glat):
			if mask[lat, lon]:
				continue
			else:
				# parameters[:, lat, lon] = DataProcess.Linear_Trend_Parameter(data[:, lat, lon])
				parameters[:, lat, lon] = DataProcess.MannKendall_Trend_Parameter(data[:, lat, lon])
	# store the parameters
	parameters.dump('%s%s/mk_trend_slope_itcpt_%s' % (workspace, varname, type))
	del data, parameters

	return

## Main function
##================
flag = 2
## Step1: Aggregate monthly time series to calculate linear trend
if flag == 1:
	types = ('ave', 'ave', 'ave', 'ave', 'ave', 'pre') # for calculating monthly value
	for i in xrange(0, len(forcing)):
		ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], styr, edyr)
		# initial month start day
		monst = stdy
		data_mon = []
		for j in xrange(0, nmon):
			# end day of the month
			moned = monst + relativedelta(months=1) - relativedelta(days=1)
			data = DataProcess.Extract_Data_Periodd_Average(monst, moned, 'open', ctl_out, varname[i], types[i])
			# Convert 2-d arrays to 3-d for stacking
			data_mon.append(data.reshape(1, glat, glon))
			del data
			# Update month
			print monst, moned
			monst = monst + relativedelta(months=1)

		# stacking all the monthly data
		data_mon = vstack(data_mon)
		if not os.path.exists('%s%s' % (workspace, varname[i])):
			os.makedirs('%s%s' % (workspace, varname[i]))
		data_mon.dump('%s%s/%s_monthly_%s-%s' %(workspace, varname[i], varname[i], styr, edyr))
		del data_mon

## Step1.5: Aggregate annual time series to calculate linear trend
if flag == 1.5:
	types = ('ave', 'ave', 'ave', 'ave', 'ave', 'pre') # for calculating monthly value
	for i in xrange(0, len(forcing)):
		ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], styr, edyr)
		# initial month start day
		data_ann = []
		for year in xrange(styr, edyr+1):
			yrst = datetime.datetime(year, 1, 1)
			yred = datetime.datetime(year, 12, 31)
			# end day of the month
			data = DataProcess.Extract_Data_Periodd_Average(yrst, yred, 'open', ctl_out, varname[i], types[i])
			# Convert 2-d arrays to 3-d for stacking
			data_ann.append(data.reshape(1, glat, glon))
			del data
			# Update month
			print yrst, yred

		# stacking all the monthly data
		data_ann = vstack(data_ann)
		if not os.path.exists('%s%s' % (workspace, varname[i])):
			os.makedirs('%s%s' % (workspace, varname[i]))
		data_ann.dump('%s%s/%s_annual_%s-%s' %(workspace, varname[i], varname[i], styr, edyr))
		del data_ann


## Step2: Get parameters from regression based on theil's slope (Mann kendall)
if flag == 2:
	for i in xrange(0, len(forcing)):
		Get_Area_Trend('annual', varname[i])

exit()

## Step3: apply the regression parameters on the

# 			data.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(1, glat, glon))
# 	data = vstack(data)
# 	data.dump('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))
#
# y - (slope * x + intercept)
# 		timeseries_update = data_detrend + ave
# 			timeseries_update.dump('%s%s/pgf_%s_detrend_%s-%s' %(workspace, var, var, lat, lon))
# 			del timeseries_update, timeseries, data_detrend

# curday = stdy
# while curday <= datetime.date(edyr, 12, 31):
# 	last_month = 1
# 	data_mon = []
#
#
# 	# if last_month is not curday.month:
# 	# 	last_month = curday.month
# 	for var in forcing:
# 		file_in = '%s%s/%s.%4d%02d%02d.nc' % (datadir, curday.year, var, curday.year, curday.month, curday.day)
# 		file_out = '%s%s/%s.detrend.%4d%02d%02d.nc' % (workspace, curday.year, var, curday.year, curday.month, curday.day)
# 		data_mon.append(Dataset(file_in).variables[var][:].reshape(1, glat, glon))
# 		data_mon = vstack(data_mon)

	# 					timeseries.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(glat, glon)[lat, lon])
	# # Create the output file
	# file_out = '%s'
	# vars = var
	# nt = 1
	# tstep = 'years'
	# fp = IO.Create_NETCDF_File(dims, file_out, var, varname, datetime.datetime(iyear, 1, 1), tstep, nt)

	# ts = Series(data_detrend, index=dates)
	# print ts[dt.datetime(1948, 12, 29):dt.datetime(1949, 1, 4)]
	#		data = load('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))

	# growing season??
