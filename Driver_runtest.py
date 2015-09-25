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
from netCDF4 import Dataset
from pylab import *
import time as tm
import pandas as pd
from pandas.tseries.offsets import Day
from pandas import Series, DataFrame
import IO, DataProcess
import sys, os, gc, calendar
gc.collect()

## import data
##------------
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
yeardir = '%syearly/' % datadir
outdir = '/home/air1/lpeng/Projects/Africa/detrend/'
prodir = '/home/air1/lpeng/Projects/Africa/Product/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
gsdir = '/home/air1/lpeng/Projects/Africa/GrowSeason/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec', 'ETo')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec', 'pet')
longname = ('Maximum Temperature', 'Minimum Temperature', 'Solar Radiation', 'Wind (10m)', 'Relative humidity', 'Precipitation', 'Reference ET')
# units = ('K', 'K', 'W/m2', 'm/s', 'x100%', 'mm/d')
glat = 292
glon = 296
styr = 2009
edyr = 2010
rsstyr = 1979
rsedyr = 2010
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

lats = linspace(dims['minlat'], dims['maxlat'], glat)
lons = linspace(dims['minlon'], dims['maxlon'], glon)

# Open mask file, mask.mask is the boolean values: True and False
mask_bl = ~Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1].mask

# load growing season calendar data
pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]

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

def Get_Area_Trend(data, filename):

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
	parameters.dump(filename)
	del data, parameters

	return

def Daily2Annual_Growseason(var, type, exps, outfilename):

	# # load growing season calendar data
	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
	# first step: create masks for two different situation, harvest day is within the same year or next year
	mask_1yr = pdate < hdate  # Boolen values
	mask_2yrs = pdate >= hdate
	# second step: create an end-day array
	edate = hdate * mask_1yr + (-1) * mask_2yrs
	# third step: initialize the 3D mask with length of 366, gsmask1 is the mask for this year, gsmask2 is the mask for next year
	gsmask1 = empty((366, glat, glon))
	gsmask1.fill(nan)
	gsmask2 = zeros((366, glat, glon))
	# fourth step: loop for each grid to slice the pdate and edate period and average
	for lat in xrange(0, glat):
		for lon in xrange(0, glon):
			if mask_bl[lat, lon]:
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
		if type == 'nc':
			data.append(nanmean(vstack((Dataset('%s%s/%s.%s.nc' %(yeardir, var, var, year)).variables[var][:] * GSmask1, Dataset('%s%s/%s.%s.nc' %(yeardir, var, var, year+1)).variables[var][:] * GSmask2)), axis=0).reshape(1, glat, glon))
		elif type == 'pk':
			data.append(nanmean(vstack((load('%s%s/%s.fullyear.%s' %(outdir, exps, var, year)) * GSmask1, load('%s%s/%s.fullyear.%s' %(outdir, exps, var, year+1)) * GSmask2)), axis=0).reshape(1, glat, glon))
		else:
			print "Error: missing data type! 'nc' for netCDF, 'pk' for pickle"
			exit(1)
		print year
	# convert to 3D annual array
	data = vstack(data)
	data.dump('%s' % outfilename)
	del data

	return

def Append_Window(year, month, day, length):

	interval = (length - 1)/2
	dates = [datetime.date(year, month, day) + relativedelta(days=d) for d in xrange(-interval, interval+1)]
	ts = Series(DataProcess.Extract_Data_Period_Average(datetime.datetime(year, month, day) - relativedelta(days=interval), datetime.datetime(year, month, day) + relativedelta(days=interval), lat, lon, 'open', ctl_out, varname[i], 'all'), index=dates)

	return ts


def blockshaped(arr, nrows, ncols):

	nt, r, c = arr.shape
	lenr = r/nrows
	lenc = c/ncols

	return array([arr[:, i*nrows:(i+1)*nrows, j*ncols:(j+1)*ncols] for i, j in ndindex(lenr, lenc)]).reshape(nt, lenr, lenc, nrows, ncols)
	# daily = blockshaped(daily, 73, 74)
	# [daily[:, x, y, :, :].dump('%s%s/annual_%s_gridbox_%02d_%02d' % (workspace, varname[i], freq, x, y)) for x in point for y in point]

## ****************************** Test Function and old code******************************
i = 6
step = 4


if step == 4:
	exps = ['start_pivot', 'end_pivot']
	# For each single day, sample an ensemble with a 7-day window across multiple years
	# choose grads only because it can get the data across two years
	# try to do it based on location instead of African spatial map
	for lat in xrange(180, 181):  #(0, glat):
		for lon in xrange(199, 200):  #(0, glon):
			ctl_out = '%s%s_%d-%d.ctl' % (datadir, forcing[i], 1948, 2010)
			# set the initial last year: control yearly data
			year = styr
			lastyear = styr - 1
			while year <= edyr:
				time = datetime.datetime.strptime('%s%03d' % (year, round(pdate[lat, lon])), '%Y%j')
				while time <= datetime.datetime.strptime('%s%03d' % (year, round(hdate[lat, lon])), '%Y%j'):
					# (1) collect the multidecade window: pool
					pool = Series()  # initialize a Series-type variable
					## the normal case
					if time.month != 2 and time.day != 29:
						for yr in xrange(rsstyr, rsedyr+1):
							pool = pool.append(Append_Window(year, time.month, time.day, 7))
					## the special case of leap year and 2.29
					else:
						for yr in xrange(rsstyr, rsedyr+1):
							if calendar.isleap(yr): 	# use Feb, 29th
								pool = pool.append(Append_Window(yr, time.month, time.day, 7))
							else:  						# resample the days using March 1st
								pool = pool.append(Append_Window(yr, 3, 1, 7))

					# (2) compare with the current day and collect the index
					index_daily = []
					doy = (time - datetime.datetime(time.year, 1, 1)).days  # day of year need adding 1, but as index for slicing, minus one again
					for j in xrange(0, 2):
						# retrieve current day
						current = Dataset('%s%s/%s/%s.fullyear.%s.nc' %(outdir, forcing[i], exps[j], forcing[i], time.year)).variables[forcing[i]][doy, lat, lon]
						# calculate the difference between the pool and the current day
						# Pick up the first 20 days with closest values
						index_daily.append(abs(pool - current).order()[1:21].index) # difference  sampling pool - current value
						# print pd.to_datetime(days[1])[0].month

					# save daily index
					if year > lastyear:
						index = []
						lastyear = year
					index.append(index_daily)

					del pool, index_daily

					# one step forward
					print time
					time = time + datetime.timedelta(days=1)

				## current year ends, new year starts
				# (3) read the variables into array for different experiments, ensembles from netcdf files
				data = [[[[Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, index[d][j][en].year, var, index[d][j][en].year,index[d][j][en].month, index[d][j][en].day)).variables[var][0, lat, lon] for en in xrange(0, 20)] for j in xrange(0, 2)] for var in forcing[:5]] for d in xrange(0, len(index))]
				data = array(data)
				## (4) save the yearly daily data into netcdf file
				filename = '%s/var.exp.ens.lat_%s_lon_%s.%4d.gs.nc' % (prodir, lats[lat], lons[lon], year)
				IO.Create_special_NETCDF_File(dims, filename, forcing[:5], longname[:5], data, time, 'days')
				del index, data
				print "save %s" %(year)
				year = year + 1

exit()

##==================================================================================
## Step4: resample code 1: for the full year
#  This function looping for each day in a year, too slow and inefficient, as we just need growing season days to be resampled
##==================================================================================
if step == 4:
	tstep = 1
	time = datetime.datetime(styr, 1, 1)
	ctl_out = '%s%s_%d-%d.ctl' % (datadir, forcing[i], 1948, edyr)
	exps = ['start_pivot', 'end_pivot']
	# For each single day, sample an ensemble with a 7-day window across multiple years
	# choose grads only because it can get the data across two years
	# try to do it based on location instead of African spatial map
	for lat in xrange(180, 181):  #(0, glat):
		for lon in xrange(199, 200):  #(0, glon):
			# set the initial last year: control yearly data
			lastyear = styr - 1
			while time <= datetime.datetime(edyr, 12, 31):

				# (1) collect the multidecade window: pool
				pool = Series()  # initialize a Series-type variable
				if time <= datetime.datetime(time.year, 12, 28):  ## the normal case
					## the normal case
					if time.month != 2 and time.day != 29:
						for year in xrange(styr, edyr+1):
							pool = pool.append(Append_Window(year, time.month, time.day, 7))
					## the special case of leap year and 2.29
					else:
						for year in xrange(styr, edyr+1):
							if calendar.isleap(year): 	# use Feb, 29th
								pool = pool.append(Append_Window(year, time.month, time.day, 7))
							else:  						# resample the days using March 1st
								pool = pool.append(Append_Window(year, 3, 1, 7))
				else:
					for year in xrange(styr, edyr):
						pool = pool.append(Append_Window(year, time.month, time.day, 7))


				# (2) compare with the current day and save
				index_daily = []
				doy = (time - datetime.datetime(time.year, 1, 1)).days  # day of year need adding 1, but as index for slicing, minus one again
				for j in xrange(0, 2):
					# retrieve current day
					current = Dataset('%s%s/%s/%s.fullyear.%s.nc' %(outdir, forcing[i], exps[j], forcing[i], time.year)).variables[forcing[i]][doy, lat, lon]
					# calculate the difference between the pool and the current day
					# Pick up the first 20 days with closest values
					index_daily.append(abs(pool - current).order()[1:21].index) # difference  sampling pool - current value
					# print pd.to_datetime(days[1])[0].month

				# save daily index
				if time.year > lastyear:
					index = []
					lastyear = time.year
				index.append(index_daily)

				del pool, index_daily

				# one step forward
				time = time + datetime.timedelta(days=1)
				tstep = tstep + 1
				print time

				# new year
				if time.year > lastyear:
					## read the variables into array for different experiments, ensembles from netcdf files
					data = [[[[Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, index[d][j][en].year, var, index[d][j][en].year,index[d][j][en].month, index[d][j][en].day)).variables[var][0, lat, lon] for en in xrange(0, 20)] for j in xrange(0, 2)] for var in forcing[:5]] for d in xrange(0, len(index))]
					data = array(data)
					## save the yearly daily data into netcdf file
					filename = '%s/var.exp.ens.lat_%s_lon_%s.%4d.nc' % (prodir, lats[lat], lons[lon], time.year-1)
					IO.Create_special_NETCDF_File(dims, filename, forcing[:5], longname[:5], data, time, 'days')
					del index, data
					print "save %s" %(time.year-1)

exit()

##==================================================================================
## Step4: resample code 2: for the full year
#  This function has bug in obtaining datetime index. It doesn't use pandas to do indexing, that's why it is difficult to deal with the leap year
# This function is also too slow since it works on high dimension array
# New function (Driver.py) will use more list comprehension / nested list and netcdf files to cut back the storage issue
# these new tricks are important, although not obvious at first glance
##==================================================================================
if step == 4.2:
	tstep = 1
	time = datetime.datetime(styr, 1, 1)
	ctl_out = '%s%s_%d-%d.ctl' % (datadir, forcing[i], 1948, edyr)
	exps = ['start_pivot', 'end_pivot']
	while time <= datetime.datetime(edyr, 12, 31):
		# (1) collect the pool
		# for the special case of leap year
		if time.day == 29 and time.month == 2:
			pool = []
			for year in xrange(styr, edyr+1):
				# use Feb, 29th
				if calendar.isleap(year):
					pool.append(DataProcess.Extract_Data_Period_Average(datetime.datetime(year, time.month, time.day) - relativedelta(days=3), datetime.datetime(year, time.month, time.day) + relativedelta(days=3), None, None, 'open', ctl_out, varname[i], 'all'))
				# resample the days using March 1st
				else:
					pool.append(DataProcess.Extract_Data_Period_Average(datetime.datetime(year, 3, 1) - relativedelta(days=3), datetime.datetime(year, 3, 1) + relativedelta(days=3), None, None, 'open', ctl_out, varname[i], 'all'))
		# for the normal case
		else:
			pool = [DataProcess.Extract_Data_Period_Average(datetime.datetime(year, time.month, time.day) - relativedelta(days=3), datetime.datetime(year, time.month, time.day) + relativedelta(days=3), None, None, 'open', ctl_out, varname[i], 'all') for year in xrange(styr, edyr+1)]

		# (2) retrieve current day map
		doy = (time - datetime.datetime(time.year, 1, 1)).days # day of year need adding 1, but as index for slicing, minus one again
		current = [Dataset('%s%s/%s/%s.fullyear.%s.nc' %(outdir, forcing[i], exps[j], forcing[i], time.year)).variables[forcing[i]][doy, :, :] * mask_bl for j in xrange(0, 2)]

		# (3) calculate the difference between the pool and the current day
		pool = vstack(pool) * mask_bl  # pool is a 3D array with time length 7*32/7*31
		dif = [abs(pool - current[j]) for j in xrange(0, 2)]
		del pool, current

		## (4) Pick up the first 20 days with closest values
		data = empty((200, glat, glon)); data.fill(nan)
		# Let's just test for one single grid cell
		data = empty((glat, glon)); data.fill(nan)
		for lat in xrange(180, 181):  #(0, glat):
			for lon in xrange(199, 200):  #(0, glon):
				if mask_bl[lat, lon]:
					# data[:, lat, lon] = sort(dif[:, lat, lon])
					## first argsort return the index of the sorted array in an increasing order
					## second argsort return the position of the sorted index in an increasing order
					## The test show that 20 ensemble members can maintain 5% error in most of the areas
					# version 1
					position = [argsort(argsort(dif[j][:, lat, lon], kind='quicksort'), kind='quicksort')[1:21] for j in xrange(0, 2)]
					days = [[datetime.date(ens//7+styr, time.month, time.day) + relativedelta(days=(ens%7-3)) for ens in position[j]] for j in xrange(0, 2)]
					# version 2
					# years = [position[j]//7+styr for j in xrange(0, 2)]
					# days = [[datetime.date(years[j][en], time.month, time.day) + relativedelta(days=(ens%7-3)) for ens in position[j]] for j in xrange(0, 2)]
					# version 3
					# position = argsort(argsort(dif[j][:, lat, lon], kind='quicksort'), kind='quicksort')[1:21]
					# years = position//7+styr
					# months = [(time + relativedelta(days=((pos)%7-3))).month for (i, pos) in enumerate(position)]
					# days = [(time + relativedelta(days=((pos)%7-3))).day for (i, pos) in enumerate(position)]

					## write to NETCDF file, for ensemble member, different variable,  and experiment
					for en in xrange(0, 20):
						if not os.path.exists('%sEnsemble%s' % (prodir, en)):
							os.makedirs('%sEnsemble%s' % (prodir, en))
						for v, var in enumerate(forcing[:5]):
							if not os.path.exists('%sEnsemble%s/%s' % (prodir, en, var)):
								os.makedirs('%sEnsemble%s/%s' % (prodir, en, var))
							for j in xrange(0, 2):
								if not os.path.exists('%sEnsemble%s/%s/%s' % (prodir, en, var, exps[j])):
									os.makedirs('%sEnsemble%s/%s/%s' % (prodir, en, var, exps[j]))
								filename = '%sEnsemble%s/%s/%s/%s.%4d%02d%02d.nc' % (prodir, en, var, exps[j], var, time.year, time.month, time.day)
								# data[lat, lon] = Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, years[en], var, years[en], months[en], days[en])).variables[var][:].reshape(glat, glon)[lat, lon]
								IO.Create_NETCDF_File(dims, filename, var, longname[v], data[:, :], time, 'days', 1)
								# print "data stored, saving to netcdf file..."

		# one step forward
		time = time + datetime.timedelta(days=1)
		tstep = tstep + 1
		print time

exit()
##==================================================================================
## Step2: aggregate annual growing season time series to calculate MK trend
#  This function looping for each grid is way too slow! just save for old code
##==================================================================================

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