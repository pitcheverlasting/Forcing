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
import IO, DataProcess, PETFAO
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
styr = 1979
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
	length = scen1 + scen2 + 1

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

def Daily2Annual_Growseason_grid(var, type, exps, outfilename):

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

	return

def Append_Window(year, month, day, length):

	"sample an ensemble with a 7-day window across multiple years. choose grads only because it can get the data across two years"
	interval = (length - 1)/2
	dates = [datetime.date(year, month, day) + relativedelta(days=d) for d in xrange(-interval, interval+1)]
	ts = Series(DataProcess.Extract_Data_Period_Average(datetime.datetime(year, month, day) - relativedelta(days=interval), datetime.datetime(year, month, day) + relativedelta(days=interval), lat, lon, 'open', ctl_out, varname[i], 'all'), index=dates)

	return ts


## ****************************** Main function ******************************
## settings
i = 6
freq = 'growseason'
step = 5

# ##=========================================
# ## Step1: calculate PET using PET FAO56 equation
# # This step is finished by Di Tian, which is in the same path
#
# ## Step2: aggregate annual growing season time series to calculate MK trend
# # (1) merge all the daily data to annual data using CDO
# if step == 2.1:
# 	outdir = '%syearly/' % datadir
# 	if not os.path.exists(outdir):
# 		os.makedirs(outdir)
# 	if not os.path.exists('%s%s' % (outdir, forcing[i])):
# 		os.makedirs('%s%s' % (outdir, forcing[i]))
# 	[os.system('~/anaconda/bin/cdo mergetime %s%s/%s*.nc %s%s/%s.%s.nc' %(datadir, year, forcing[i], outdir, forcing[i], forcing[i], year)) for year in xrange(styr, edyr+1)]
#
#
# # (2) aggregate annual growing season time series
# if step == 2.2:
# 	# load growing season calendar data
# 	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
# 	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
# 	## ultimate goal: make a 3D mask that get all the growing season values
# 	# first step: create masks for two different situation, harvest day is within the same year or next year
# 	mask_1yr = pdate < hdate  # Boolen values
# 	mask_2yrs = pdate >= hdate
# 	# second step: create an end-day array, when the harvest day is within the same year, just make the end day the same as the harvest day; when the harvest day is in the next year, just make the end day as the last day of the year
# 	edate = hdate * mask_1yr + (-1) * mask_2yrs
# 	# third step: initialize the 3D mask with length of 366, msmask1 is the mask for this year, gsmask2 is the mask for next year
# 	gsmask1 = empty((366, glat, glon))
# 	gsmask1.fill(nan)
# 	gsmask2 = zeros((366, glat, glon))
# 	# fourth step: loop for each grid to slice the pdate and edate period and average
# 	for lat in xrange(0, glat):
# 		for lon in xrange(0, glon):
# 			if mask_bl[lat, lon]:
# 				gsmask1[pdate[lat, lon]:edate[lat, lon], lat, lon] = 1
# 				gsmask2[:hdate[lat, lon], lat, lon] = 1
# 	gsmask2 = gsmask2 * mask_2yrs; gsmask2[gsmask2==0.0] = nan
# 	data = []
# 	for year in xrange(styr, edyr): # since the end of growing season may exceed the last year
# 		if calendar.isleap(year):
# 			GSmask1 = gsmask1
# 		else:
# 			GSmask1 = gsmask1[:365, :, :]
# 		if calendar.isleap(year+1):
# 			GSmask2 = gsmask2
# 		else:
# 			GSmask2 = gsmask2[:365, :, :]
# 		# data = vstack((Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year)).variables[forcing[i]][:] * GSmask1, Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year+1)).variables[forcing[i]][:] * GSmask2))
# 		# aggregate to annual growing season values by adding the two years together
# 		data.append(nanmean(vstack((Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year)).variables[forcing[i]][:] * GSmask1, Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year+1)).variables[forcing[i]][:] * GSmask2)), axis=0).reshape(1, glat, glon))
# 		print year
# 	# convert to 3D annual array
# 	data = vstack(data)
# 	data.dump('%s%s/%s_%s_%s-%s' %(workspace, varname[i], varname[i], freq, styr, edyr))
#
# # (3) calculate MK trend
# if step == 2.3:
# 	data = load('%s%s/%s_%s_%s-%s' %(workspace, varname[i], varname[i], freq, styr, edyr))
# 	filename = '%s%s/mk_trend_slope_st_ed_%s' % (workspace, varname[i], freq)
# 	Get_Area_Trend(data, filename)
#
# ## Step3: detrend the PET according to the two pivots experiments
# if step == 3:
# 	parameters = load('%s%s/mk_trend_slope_st_ed_%s' % (workspace, varname[i], freq))
# 	firstyr = datetime.date(styr, 1, 1) # to calculate the starting index
# 	# loop for each year to read data
# 	for year in xrange(styr, edyr+1):
# 		yrst = datetime.date(year, 1, 1)
# 		nxyrst = datetime.date(year+1, 1, 1)
# 		nd = (nxyrst-yrst).days
# 		x = np.arange(nd, dtype=float) + (yrst - firstyr).days
# 		# This is to extend 1D time dimension horizontally to 3D array
# 		X = tile(x, glat * glon).reshape(glat, glon, nd).swapaxes(0, 2).swapaxes(1, 2)
# 		Y = Dataset('%s%s/%s.%s.nc' %(yeardir, forcing[i], forcing[i], year)).variables[forcing[i]][:]
# 		# EXP1: start pivot
# 		exp1 = Y - parameters[0, :, :]/365.25 * X
# 		# EXP2: end pivot
# 		exp2 = Y - parameters[0, :, :]/365.25 * X - parameters[1, :, :] + parameters[2, :, :]
# 		exp1.dump('%sstart_pivot/%s.fullyear.%s' %(outdir, forcing[i], year))
# 		exp2.dump('%send_pivot/%s.fullyear.%s' %(outdir, forcing[i], year))
# 		del X, Y, exp1 , exp2
# 		print year
#
# ## aggregate annual growing season time series for the two pivots experiments
# if step == 3.1:
# 	exps = 'start_pivot'
# 	outfilename = '%s%s/%s_detrend_%s_%s_%s-%s' %(workspace, varname[i], varname[i], exps, freq, styr, edyr)
# 	Daily2Annual_Growseason(var, 'pk', exps, outfilename)


# ## Step4: resample from the PET
# if step == 4:
# 	# load growing season calendar data
# 	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
# 	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
# 	exps = ['start_pivot', 'end_pivot']
# 	# try to do it based on location instead of African spatial map
# 	for lat in xrange(180, 181):  #(0, glat):
# 		for lon in xrange(199, 200):  #(0, glon):
# 			ctl_out = '%s%s_%d-%d.ctl' % (datadir, forcing[i], 1948, 2010)
# 			# set the initial last year: control yearly data
# 			year = styr
# 			lastyear = styr - 1
# 			while year <= edyr:
# 				time = datetime.datetime.strptime('%s%03d' % (year, round(pdate[lat, lon])), '%Y%j')
# 				while time <= datetime.datetime.strptime('%s%03d' % (year, round(hdate[lat, lon])), '%Y%j'):
# 					# (1) For each single day, sample an ensemble with a 7-day window across multiple years
# 					pool = Series()  # initialize a Series-type variable for the multidecade window
# 					## the normal case
# 					if time.month != 2 and time.day != 29:
# 						for yr in xrange(rsstyr, rsedyr+1):
# 							pool = pool.append(Append_Window(year, time.month, time.day, 7))
# 					## the special case of leap year and 2.29
# 					else:
# 						for yr in xrange(rsstyr, rsedyr+1):
# 							if calendar.isleap(yr): 	# use Feb, 29th
# 								pool = pool.append(Append_Window(yr, time.month, time.day, 7))
# 							else:  						# resample the days using March 1st
# 								pool = pool.append(Append_Window(yr, 3, 1, 7))
#
# 					# (2) compare with the current day and collect the index
# 					index_daily = []
# 					doy = (time - datetime.datetime(time.year, 1, 1)).days  # day of year need adding 1, but as index for slicing, minus one again
# 					for j in xrange(0, 2):
# 						# retrieve current day
# 						current = Dataset('%s%s/%s/%s.fullyear.%s.nc' %(outdir, forcing[i], exps[j], forcing[i], time.year)).variables[forcing[i]][doy, lat, lon]
# 						# calculate the difference between the pool and the current day
# 						# Pick up the first 20 days with closest values
# 						index_daily.append(abs(pool - current).order()[1:21].index) # difference  sampling pool - current value
# 						# print pd.to_datetime(days[1])[0].month
#
# 					# save daily index
# 					if year > lastyear:
# 						index = []
# 						lastyear = year
# 					index.append(index_daily)
#
# 					del pool, index_daily
#
# 					# one step forward
# 					print time
# 					time = time + datetime.timedelta(days=1)
#
# 				## current year ends, new year starts
# 				# (3) read the variables into array for different experiments, ensembles from netcdf files
# 				data = [[[[Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, index[d][j][en].year, var, index[d][j][en].year,index[d][j][en].month, index[d][j][en].day)).variables[var][0, lat, lon] for en in xrange(0, 20)] for j in xrange(0, 2)] for var in forcing[:5]] for d in xrange(0, len(index))]
# 				data = array(data)
# 				## (4) save the yearly daily data into netcdf file
# 				filename = '%s/var.exp.ens.lat_%s_lon_%s.%4d.gs.nc' % (prodir, lats[lat], lons[lon], year)
# 				IO.Create_special_NETCDF_File(dims, filename, forcing[:5], longname[:5], data, time, 'days')
# 				del index, data
# 				print "save %s" %(year)
# 				year = year + 1
#
# exit()
# ##=========================================
# ## Step5: calculate new PET using PET FAO56 equation
if step == 5:
	# load growing season calendar data
	pdate = Dataset('%smzplant_mu.nc' % gsdir).variables['pmu'][::-1]
	hdate = Dataset('%smzharvest_mu.nc' % gsdir).variables['hmu'][::-1]
	# read the growing season detrended climate variables
	for lat in xrange(180, 181):  #(0, glat):
		for lon in xrange(199, 200):  #(0, glon):
			INPUT = {}
			INPUT['lat'] = lats[lat]
			INPUT['gslen'] = Get_Growseason_Length(round(pdate[lat, lon]), round(hdate[lat, lon]))
			INPUT['doy'] = linspace(round(pdate[lat, lon]), round(hdate[lat, lon]), INPUT['gslen'])
			for var in forcing[:5]:
				data = vstack([Dataset('%s/var.exp.ens.lat_%s_lon_%s.%4d.gs.nc' % (prodir, lats[lat], lons[lon], year)).variables[var][:] for year in xrange(styr, edyr+1)])  # vstack: convert data into 3D array, 1 dimension is the time series
				INPUT[var] = data
				del data


			## (1) calculate PET using PETFAO
			ETo_detrend = PETFAO.Data(INPUT).ETo_FAO56
			# numbers of year, growing season days in each year, exp, ens
			ETo_detrend_annual = mean(ETo_detrend.reshape(ETo_detrend.shape[0] / INPUT['gslen'], INPUT['gslen'], ETo_detrend.shape[1], ETo_detrend.shape[2]), axis=1)
			# ETo_rs_start = mean(ETo_detrend_annual[:-2,0,:], axis=1)
			# ETo_rs_end = mean(ETo_detrend_annual[:-2,1,:], axis=1)
			ETo_rs_start = ETo_detrend_annual[:-2,0,0]
			ETo_rs_end = ETo_detrend_annual[:-2,1,0]
			## (2) origin ETo data
			st = int(round(pdate[lat, lon])-1)
			ed = int(round(hdate[lat, lon]))
			origin = [mean(Dataset('%s%s/%s.%s.nc' % (yeardir, forcing[6], forcing[6], year)).variables[forcing[6]][st:ed,  lat, lon], axis=0) for year in xrange(styr, edyr)]
			origin = vstack(origin)

			## (3) trend removal
			start = load('%s%s/%s_detrend_%s_%s_%s-%s' %(workspace, varname[6], varname[6], 'start_pivot', freq, styr, edyr))[:-1, lat, lon]
			end = load('%s%s/%s_detrend_%s_%s_%s-%s' %(workspace, varname[6], varname[6], 'end_pivot', freq, styr, edyr))[:-1, lat, lon]

			# Plot figure
			plt.plot(start, label='detrend:start', color='red', linewidth=3.0, linestyle='--')
			plt.plot(end, label='detrend:end', color='blue', linewidth=3.0, linestyle='--')
			plt.plot(ETo_rs_start, label='resampled:start', color='red', linewidth=3.5)
			plt.plot(ETo_rs_end, label='resampled:end', color='blue', linewidth=3.5)
			plt.plot(origin[:-1], label='origin', color='black', linewidth=3.0, marker='o')
			ticks = arange(1979, 2011)
			plt.legend(prop={'size':24}, ncol=3, loc=3)
			plt.xlim([-1,len(start)])
			plt.xticks(range(len(ticks))[1::5], ticks[1::5], fontsize=28)
			plt.yticks(arange(3.2,4.5,0.2),fontsize=28)
			plt.ylabel('PET [mm/d]', fontsize=28)
			plt.show()


# calculate ensemble mean
exit()


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

