__author__ = 'lpeng'

from netCDF4 import Dataset
from pylab import *
import calendar
import IO

## start GrADS
##------------
sys.path.insert(0, "/home/water5/lpeng/python/mylib/")
from grads import *
from gradsen import *
gradsen()
ga = GrADS(Bin='/home/latent2/mpan/local/opengrads/Linux/x86_64/grads', Verb=False, Echo=False, Port=False, Window=False, Opts="-c 'q config'")


def Extract_Data_Periodd_Average(idate_out, fdate_out, open_type, ctl_in, var, type):

	# open access to the control file
	ga("%s %s" % (open_type, ctl_in))
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
