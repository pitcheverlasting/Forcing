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
import sys, os, gc, time, calendar
from netCDF4 import Dataset
from pylab import *
import IO, DataProcess
gc.collect()

# a = [3, 35, 23, 8, 64,1, 9, 45]
# print argsort(a, kind='quicksort'),'1'
# print argsort(argsort(a, kind='quicksort'), kind='quicksort'),'2'
## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
outdir = '/home/air1/lpeng/Projects/Africa/detrend/'
gsdir = '/home/air1/lpeng/Projects/Africa/GrowSeason/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec', 'ETo')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec', 'pet')
units = ('K', 'K', 'W/m2', 'm/s', 'x100%', 'mm/d')

glat = 292
glon = 296
styr = 1979
edyr = 2010
stdy = datetime.date(styr, 1, 1)
eddy = datetime.date(edyr, 12, 31)
# nt = (eddy - stdy).days + 1
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

# Open mask file : this mask is different from Lyndon's mask
# maskdir = '/home/water5/lpeng/Masks/0.25deg/africa/'
# # mask.mask is the boolean values: True and False
# mask_bl = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :].mask
# mask = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :]
mask_bl = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1].mask

print 2e-5 * 600
exit()
i=6

for year in xrange(styr+2, edyr+1):
	file1 = '%s%s/start_pivot/%s.fullyear.%s.nc' %(outdir, forcing[i],forcing[i], year)
	file2 = '%s%s/end_pivot/%s.fullyear.%s.nc' %(outdir, forcing[i], forcing[i], year)
	tinitial = datetime.datetime(year, 1, 1)
	start = load('%sstart_pivot/%s.fullyear.%s' %(outdir, forcing[i], year))
	nt = start.shape[0]
	IO.Create_NETCDF_File(dims, file1, 'ETo', 'reference ET: detrending starting point pivotal experiment',start, tinitial, 'days', nt)
	del start
	end = load('%send_pivot/%s.fullyear.%s' %(outdir, forcing[i], year))
	IO.Create_NETCDF_File(dims, file2, 'ETo', 'reference ET: detrending ending point pivotal experiment', end, tinitial, 'days', nt)
	del end
	print year

exit()

def blockshaped(arr, nrows, ncols):

	nt, r, c = arr.shape
	lenr = r/nrows
	lenc = c/ncols

	return array([arr[:, i*nrows:(i+1)*nrows, j*ncols:(j+1)*ncols] for i, j in ndindex(lenr, lenc)]).reshape(nt, lenr, lenc, nrows, ncols)
	# daily = blockshaped(daily, 73, 74)
	# [daily[:, x, y, :, :].dump('%s%s/annual_%s_gridbox_%02d_%02d' % (workspace, varname[i], freq, x, y)) for x in point for y in point]

## ****************************** Main function ******************************

step = 2
##=========================================
## Step1: calculate PET using PET FAO56 equation
# This step is finished by Di Tian, which is in the same path

# This function looping for each grid is way too slow! just save for old code
## Step2: aggregate annual growing season time series to calculate MK trend
if step == 2:
	i = 6
	type = 'pre'  # aggregating method for both PET and P
	ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], 1948, edyr)
	# load growing season calendar data
	freq = 'growseason'
	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
	parameters = empty((3, glat, glon))
	parameters.fill(nan)
	for lon in xrange(0, glon):
		for lat in xrange(0, glat):
			if mask_bl[lat, lon]:
				continue
			else:
				data_append = []
				for year in xrange(styr, edyr): # since the end of growing season may exceed the last year
					stdy = datetime.datetime.strptime(str(year)+str(int(round(pdate[lat, lon]))), '%Y%j')
					gsyr = (pdate[lat, lon] >= hdate[lat, lon]) * (year+1) + (pdate[lat, lon] < hdate[lat, lon]) * year   # This condition argument is good for numbers only
					eddy = datetime.datetime.strptime(str(gsyr)+str(int(round(hdate[lat, lon]))), '%Y%j')
					data_append.append(DataProcess.Extract_Data_Period_Average(stdy, eddy, lat, lon, 'open', ctl_out, varname[i], type))
				data_append = vstack(data_append).reshape(-1)
				parameters[:, lat, lon] = DataProcess.MannKendall_Trend_Parameter(data_append)
				print lat, lon

	parameters.dump('%s%s/mk_trend_slope_st_ed_%s' % (workspace, varname, freq))
	# parameters[:, lat, lon] = DataProcess.MannKendall_Trend_Parameter(data_append)

# data = load('%spet/pet_growseason_1979-2010' %(workspace))
# plt.plot(nanmean(nanmean(data, axis=2), axis=1))
# plt.show()
exit()
