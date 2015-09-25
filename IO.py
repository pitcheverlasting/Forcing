import netCDF4 as netcdf
import numpy as np
import datetime, sys, os
## start GrADS
##------------
sys.path.insert(0, "/home/water5/lpeng/Programming/python/mylib/")
from grads import *
from gradsen import *
gradsen()
ga = GrADS(Bin='/home/latent2/mpan/local/opengrads/Linux/x86_64/grads', Verb=False, Echo=False, Port=False, Window=False, Opts="-c 'q config'")

def Create_NETCDF_File(dims, file, var, varname, data, tinitial, tstep, nt):

	nlat = dims['nlat']
	nlon = dims['nlon']
	res = dims['res']
	minlon = dims['minlon']
	minlat = dims['minlat']
	undef = dims['undef']
	t = np.arange(0, nt)

	# Prepare the netcdf file
	# Create file
	f = netcdf.Dataset(file, 'w', format='NETCDF4')

	# Define dimensions
	f.createDimension('lon', nlon)
	f.createDimension('lat', nlat)
	f.createDimension('t', len(t))

	# Longitude
	f.createVariable('lon', 'd', ('lon',))
	f.variables['lon'][:] = np.linspace(minlon, minlon+res*(nlon-1), nlon)
	f.variables['lon'].units = 'degrees_east'
	f.variables['lon'].long_name = 'Longitude'
	f.variables['lon'].res = res

	# Latitude
	f.createVariable('lat', 'd', ('lat',))
	f.variables['lat'][:] = np.linspace(minlat, minlat+res*(nlat-1), nlat)
	f.variables['lat'].units = 'degrees_north'
	f.variables['lat'].long_name = 'Latitude'
	f.variables['lat'].res = res

	# Time
	f.createVariable('t', 'd', ('t', ))
	f.variables['t'][:] = t
	f.variables['t'].units = '%s since %04d-%02d-%02d %02d:00:00.0' % (tstep,tinitial.year,tinitial.month,tinitial.day,tinitial.hour)
	f.variables['t'].long_name = 'Time'

	# Data
	datafield = f.createVariable(var, 'f', ('t', 'lat', 'lon',), fill_value=undef, zlib=True)
	f.variables[var].long_name = varname
	datafield[:] = data

	f.sync()
	f.close()

	return #f


def Create_special_NETCDF_File(dims, file, vars, varname, data, tinitial, tstep):

	nt = data.shape[0]
	nexp = data.shape[2]
	ns = data.shape[3]
	undef = dims['undef']
	t = np.arange(0, nt)

	# Prepare the netcdf file
	# Create file
	f = netcdf.Dataset(file, 'w', format='NETCDF4')

	# Define dimensions
	f.createDimension('t', len(t))
	f.createDimension('experiment', nexp)
	f.createDimension('ensemble', ns)

	# Time
	f.createVariable('t', 'd', ('t', ))
	f.variables['t'][:] = t
	f.variables['t'].units = '%s since %04d-%02d-%02d %02d:00:00.0' % (tstep,tinitial.year,tinitial.month,tinitial.day,tinitial.hour)
	f.variables['t'].long_name = 'Time'

	# Data
	for v, var in enumerate(vars):
		datafield = f.createVariable(var, 'f', ('t', 'experiment', 'ensemble',), fill_value=undef, zlib=True)
		f.variables[var].long_name = varname
		datafield[:] = data[:, v, :, :]

	f.sync()
	f.close()


def Write_NETCDF_File(dims, file, var, varname, tinitial, tstep, nt):

	f = netcdf.Dataset(file, 'a')
	date_time = f.variables['time']

	return

def Binary2netcdf(dir_in, dir_out, file_in, file_out):

	str = 'cdo -r -f nc import_binary %s%s %s%s' % (dir_in, file_in, dir_out, file_out)
	os.system(str)

	return

def Create_Binary_File(ctl_in, filename, dims):

	ga('open %s' % ctl_in)
	ga('set lon %s %s' % (dims['minlon'], dims['maxlon']))
	ga('set lat %s %s' % (dims['minlat'], dims['maxlat']))
	ga('set t 1')
	ga('set gxout fwrite')
	ga('set fwrite %s' % filename)
	ga('d data')
	ga('disable fwrite')

	return

def Create_Geotiff_File(b):

	a = b

	return a


def Create_Control_File(type, dims, stdy, nt, tstep, var, varname, file_template, ctl_file):

	fp = open(ctl_file, 'w')
	fp.write('dset %s\n' % file_template)
	if type == 'nc':
		fp.write('dtype netcdf\n')
		fp.write('undef %s\n' % dims['undef'])
		fp.write('options template\n')
		fp.write('xdef %d linear %f %f\n' %(dims['nlon'], dims['minlon'], dims['res']))
		fp.write('ydef %d linear %f %f\n' % (dims['nlat'], dims['minlat'], dims['res']))
		fp.write('zdef 1 levels 0\n')  # This line is easily forgotten
		fp.write('tdef %d linear %s %s\n' %(nt, datetime2gradstime(stdy), tstep))
		fp.write('vars 1\n')
		fp.write('%s=>%s 0 t,y,x %s\n' %(var, varname, varname))  # This line is really important. translate nc file into grads readable file
	if type == 'mask':
		fp.write('undef %s\n' % dims['undef'])
		fp.write('options little_endian\n')
		fp.write('xdef %d linear %f %f\n' %(dims['nlon'], dims['minlon'], dims['res']))
		fp.write('ydef %d linear %f %f\n' % (dims['nlat'], dims['minlat'], dims['res']))
		fp.write('zdef 1 levels 0\n')  # This line is easily forgotten
		fp.write('tdef 1 linear %s 1mo\n' %datetime2gradstime(stdy))
		fp.write('vars 1\n')
		fp.write('data 0 99 Mask\n')

	fp.write('endvars\n')
	fp.close()

	return

### This is not a function, it's a usage of function
def Create_Control_File_Loop(datadir, styr, edyr, forcing, dims, nt, var, varname):
	# Create the control file
	type = "nc"
	stdy = datetime.datetime(styr, 1, 1)
	tstep = '1dy'
	for i in xrange(0, len(forcing)):
		ctl_out = '%s/%s_%d-%d.ctl' % (datadir, forcing[i], styr, edyr)
		file_template = '%s%s/%s.%s%s%s.nc' % (datadir,'%y4', var, '%y4', '%m2', '%d2')
		Create_Control_File(type, dims, stdy, nt, tstep, var, varname[i], file_template, ctl_out)


def datetime2gradstime(date):

	# Convert dtetime to grads time
	str = date.strftime('%HZ%d%b%Y')

	return str

def gradstime2datetime(str):

	# Convert grads time to datetime
	date = datetime.datetime.strptime(str, '%HZ%d%b%Y')

	return date