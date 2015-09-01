__author__ = 'lpeng'

from netCDF4 import Dataset
from pylab import *
import calendar
import IO
from scipy import stats

## start GrADS
##------------
sys.path.insert(0, "/home/water5/lpeng/python/mylib/")
from grads import *
from gradsen import *
gradsen()
ga = GrADS(Bin='/home/latent2/mpan/local/opengrads/Linux/x86_64/grads', Verb=False, Echo=False, Port=False, Window=False, Opts="-c 'q config'")


def Extract_Data_Period_Average(idate_out, fdate_out, lat, lon, open_type, ctl_in, var, type):

	# open access to the control file
	ga("%s %s" % (open_type, ctl_in))
	# determine spatial domain
	if lat is not None and lon is not None:
		ga('set x %s' % (lon+1))
		ga('set y %s' % (lat+1))
	# determine initial and final time step
	ga('set t 1')
	idate_all = IO.gradstime2datetime(ga.exp(var).grid.time[0])
	ga('set t last')
	fdate_all = IO.gradstime2datetime(ga.exp(var).grid.time[0])

	if idate_out >= idate_all and fdate_out <= fdate_all:
		t1 = IO.datetime2gradstime(idate_out)
		t2 = IO.datetime2gradstime(fdate_out)
	else:
		t1 = IO.datetime2gradstime(idate_all)
		t2 = IO.datetime2gradstime(fdate_all)

	# Extract data
	if type == 'ave':
		ga('datos = ave(%s, time=%s, time=%s)' %(var, t1, t2))
		data = ma.getdata(ga.exp('maskout(datos, datos)'))

	elif type == 'pre':
		ga('set time %s %s' %(t1, t2))
		data = ma.getdata(ga.exp('maskout(%s, %s)' % (var, var)))
		data[data<-9999] = nan
		data = nansum(data, axis=0)

	elif type == 'all':
		ga('set time %s %s' %(t1, t2))
		data = ma.getdata(ga.exp('maskout(%s, %s)' % (var, var)))

	else:
		print "Error: wrong type. Please select ave, pre, or all"

	# Close access to the grads data
	ga('close 1')

	return data


def MannKendall_Trend_Parameter(y):

	""" Use Theil-Sen slope to calculate the median (nonparametric) trend """
	y = np.asarray(y)
	if y.ndim > 1:
		raise ValueError('y cannot have ndim > 1')
	if not y.ndim:
		return np.array(0., dtype=y.dtype)
	x = np.arange(y.size, dtype=float)
	b = stats.mstats.theilslopes(y, alpha=0.95)[0]  # Recall that mstats use alpha=0.95 but stats use alpha=0.05
	# corr, p = stats.mstats.kendalltau(x, y)
	a = mean(y) - b*mean(x)
	# to get the starting point and ending point
	st = b * x[0] + a
	ed = b * x[-1] + a

	# In this case, I use annual value to detrend daily values, so annual unit slope is converted into daily unit by deviding 365.25
	return [b, st, ed]

def Linear_Trend_Parameter(y):

	y = np.asarray(y)
	if y.ndim > 1:
		raise ValueError('y cannot have ndim > 1')
	if not y.ndim:
		return np.array(0., dtype=y.dtype)

	x = np.arange(y.size, dtype=float)

	C = np.cov(x, y, bias=1)
	b = C[0, 1]/C[0, 0]
	a = mean(y) - b*mean(x)

	return [a, b]


## The following functions are slow functions
## ==================Old Zone===========================

def Assemble_grid_daily_timeseries(datadir, workspace, forcing, styr, edyr, glat, glon):

	## load daily data into single file for detrending for each grid
	for var in forcing:
		if not os.path.exists('%s%s' % (workspace, var)):
			os.makedirs('%s%s' % (workspace, var))
		for lon in xrange(0, glon):
			for lat in xrange(0, glat):
				timeseries = []
				for year in xrange(styr, edyr+1):
					if calendar.isleap(year):
						nd = 366
						print lon, year
					else:
						nd = 365
					stdy = datetime.date(year, 1, 1)
					for d in xrange(0, nd):
						curdy = stdy + datetime.timedelta(d)
						timeseries.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(glat, glon)[lat, lon])

				timeseries = array(timeseries)

				# 1st: use detrend in mlab
				data_detrend = mlab.detrend_linear(timeseries)
				ave = np.mean(timeseries)
				timeseries_update = data_detrend + ave
				timeseries_update.dump('%s%s/pgf_%s_detrend_%s-%s' %(workspace, var, var, lat, lon))
				del timeseries_update, timeseries, data_detrend

	return


def Assemble_areal_daily_timeseries(datadir, workspace, forcing, styr, edyr, glat, glon):

	## load daily data into single file for detrending
	for var in forcing:
		data = []
		for year in xrange(styr, edyr+1):
			if calendar.isleap(year):
				nd = 366
			else:
				nd = 365
			stdy = datetime.date(year, 1, 1)
			for d in xrange(0, nd):
				curdy = stdy + datetime.timedelta(d)
				data.append(Dataset('%s%s/%s.%4d%02d%02d.nc' % (datadir, year, var, year, curdy.month, curdy.day)).variables[var][:].reshape(1, glat, glon))
		data = vstack(data)
		data.dump('%spgf_%s_africa_daily_%s-%s' %(workspace, var, styr, edyr))

	return
