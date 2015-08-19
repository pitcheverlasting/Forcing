#!/usr/bin/env python
__author__ = 'lpeng'

from netCDF4 import Dataset
from pylab import *
from PlotLibrary import Mapshow
import datetime as dt
import calendar, IO
import pickle

##========Path===================================
datadir = '/home/air1/lpeng/Projects/Africa/Data/'
workspace = '/home/air1/lpeng/Projects/Africa/workspace/'
forcing = ('Tmax', 'Tmin', 'Rs', 'wnd10m', 'RH', 'prec')
varname = ('tmax', 'tmin', 'rs', 'wind', 'rh', 'prec')

##========dimension=========================
glat = 292
glon = 296
styr = 1948
edyr = 2010
stdy = datetime.datetime(styr, 1, 1)
eddy = datetime.datetime((edyr), 12, 31)
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

# ##========Function for Reading DGA station data information==========
def CreateMask(maskdir, dims, type):

	ctl_in = '%smask_continent_africa.ctl' %maskdir
	filename = '%smask_continent_africa_crop.bin' %maskdir
	ctl_out = '%smask_continent_africa_crop.ctl' %maskdir
	IO.Create_Binary_File(ctl_in, filename, dims)
	IO.Create_Control_File('mask', dims, stdy, None, None, None, None, filename, ctl_out)
	if type == 'nc':
		IO.Binary2netcdf(maskdir, maskdir, 'mask_continent_africa_crop.ctl', 'mask_continent_africa_crop.nc')

	return

def TimeGet(file_in, num_records):
	data_in = np.loadtxt(file_in, skiprows=12, usecols=(2,), dtype={'names': ('time',), 'formats': ('S1000',)})
	unix_time = []
	if num_records > 1:
		for date in data_in['time']:
			tmp = calendar.timegm(datetime.datetime.strptime(date, '%Y%m%d').timetuple())
			unix_time.append(tmp)
	elif num_records == 1:
		tmp = calendar.timegm(datetime.datetime.strptime(data_in.item()[0], '%Y%m%d').timetuple())
		unix_time.append(tmp)

	#print datetime.datetime.utcfromtimestamp(tmp),date
	unix_time = np.array(unix_time)

	return unix_time

def PrecGet(file_in, num_records):
	data_in = np.loadtxt(file_in, skiprows=12, usecols=(9,), dtype={'names': ('prec',), 'formats': ('S1000',)})
	#Precipitation (mm/day)
	prec_data = []
	prec_flag = []
	prec = data_in['prec']

	if num_records > 1:
		for val in prec:
			if val == '99.99':
				prec_data.append(float('NaN'))
				prec_flag.append('NaN')
			else:
				prec_data.append(float(val[0:-1:]))
				prec_flag.append(val[-1])
	elif num_records == 1:
		if prec == '99.99':
			prec_data.append(float('NaN'))
			prec_flag.append('NaN')
		else:
			prec_data.append(float(prec.item()[0:-1:]))
			prec_flag.append(prec.item()[-1])
	#
	prec_data = np.array(prec_data)
	prec_data = 25.4 * prec_data

	return prec_data


##==============Main Function===============
# Open mask file
maskdir = '/home/water5/lpeng/Masks/0.25deg/africa/'
mask = Dataset('%smask_continent_africa_crop.nc' %maskdir).variables['data'][0, :, :]  # this is for computing
units = ('[$K$$\cdot$$decade^{-1}$]', '[$K$$\cdot$$decade^{-1}$]', '[$W$$\cdot$$m^{-2}$$\cdot$$decade^{-1}$]', '[$m$$\cdot$$s$$decade^{-1}$]', '[%$\cdot$$decade^{-1}$]', '[$mm$$\cdot$$yr^{-2}$]')
limits = ([-0.25, -0.25], [-0.25, 0.25], [-2., 2.], [-0.1, 0.1], [-1., 1.], [-20., 20.])
factors = [10, 10, 10, 10, 1000, 1.]
for i in xrange(0, len(forcing)):
	# slope1 = load('%s%s/trend_slope_itcpt' % (workspace, varname[i]))
	# slope2 = load('%s%s/mk_trend_slope_itcpt_p_corr' % (workspace, varname[i]))
	slope = load('%s%s/mk_trend_slope_itcpt_annual' % (workspace, varname[i]))
	title = 'trend slope of %s' % varname[i]
	Mapshow(dims, slope[1, :, :]*mask*factors[i], None, None,limits[i][0], limits[i][1], title, units[i])
	# Mapshow(dims, data, clevs, cblevs, max, min, tit, unit)
	# look at pe nldas drawing
	# again, redo the calculation of pe attribution
	# redo the four dimension figure



# #=========Statistics about the station===========
# read the data from the didctionary format using pickle
# stflag = 0
# if stflag == 1:
# 	station = pickle.load(open('%schile_stationlist' %workspace, "rb"))
#
# 	for istation in xrange(0, len(station)):
# 		precdata = np.array(station[istation]['prec'])[:]
# 		idx = np.where(np.isnan(precdata)==0)
# 		missingidx = np.isnan(precdata[idx[0][0]:idx[0][len(idx[0])-1]])
# 		missingdays = sum(missingidx)
# 		station[istation]['stdy'] = datetime.datetime.utcfromtimestamp(station[istation]['unix_time'][idx[0][0]])
# 		station[istation]['eddy'] = datetime.datetime.utcfromtimestamp(station[istation]['unix_time'][idx[0][len(idx[0])-1]])
# 		station[istation]['stdy_year'] = station[istation]['stdy'].year
# 		station[istation]['eddy_year'] = station[istation]['eddy'].year
# 		station[istation]['data_length'] = station[istation]['eddy_year'] - station[istation]['stdy_year'] + 1
# 		duration = (station[istation]['eddy'] - station[istation]['stdy']).days
# 		station[istation]['effect_percentage'] = (duration - missingdays) / float(duration) * 100
#
# 	with open('%schile_station_evaluation' %workspace, 'wb') as handle:
# 		pickle.dump(station, handle)
#
# plot_flag = 1
# if plot_flag == 1:
# 	station = pickle.load(open('%schile_station_evaluation' %workspace, "rb"))
# 	eff = []; lons = []; lats = []; styear = []; edyear = []; length = []
# 	for istation in xrange(0, len(station)):
# 		eff.append(station[istation]['effect_percentage'])
# 		lons.append(station[istation]['lon'])
# 		lats.append(station[istation]['lat'])
# 		styear.append(station[istation]['stdy_year'])
# 		edyear.append(station[istation]['eddy_year'])
# 		length.append(station[istation]['data_length'])
# 	eff = vstack(eff); lons = vstack(lons); lats = vstack(lats); styear = vstack(styear); edyear = vstack(edyear); length = vstack(length)
# 	# CateScatter(eff, lons, lats, 'Effective data percentile', '[%]', '%sstation/GSOD/' %figdir, 'effective_percentile_map')
# 	Scatter(styear, lons, lats, None, None, plt.cm.jet, 'Starting year of GSOD stations (1950-2012)', 'Starting Year', '%sstation/GSOD/' %figdir, 'start_year_record_map')
# 	Scatter(edyear, lons, lats, None, None, plt.cm.jet, 'Ending year of GSOD stations (1950-2012)', 'Ending Year', '%sstation/GSOD/' %figdir, 'end_year_record_map')
# 	Scatter(length, lons, lats, None, None, plt.cm.jet, 'Record years of GSOD stations (1950-2012)', 'Number of records (year)', '%sstation/GSOD/' %figdir, 'years_record_map')


# styear = [(stdy + dt.timedelta(st[i][0])).year for i in range(723)]
# styear = vstack(styear)
# edyear = [(stdy + dt.timedelta(ed[i][0])).year for i in range(723)]
# edyear = vstack(edyear)
#
# #=========Mapping================================
#
# data = prec[:, stdate:eddate].reshape(723, (eddate-stdate)/365, 365)
# plt.imshow(data[222, :, :])
# plt.colorbar()
# plt.show()
exit()
