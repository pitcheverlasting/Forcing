__author__ = 'lpeng'
from pylab import *
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap

# use imshow
# Chile: -66 to -81: 15*4=60: lon; -17 to -56: 39*4=156: lat
nws_precip_colors = [
	"#04e9e7",  # 0.01 - 0.10 inches
	"#019ff4",  # 0.10 - 0.25 inches
	"#0300f4",  # 0.25 - 0.50 inches
	"#02fd02",  # 0.50 - 0.75 inches
	"#01c501",  # 0.75 - 1.00 inches
	"#008e00",  # 1.00 - 1.50 inches
	"#fdf802",  # 1.50 - 2.00 inches
	"#e5bc00",  # 2.00 - 2.50 inches
	"#fd9500",  # 2.50 - 3.00 inches
	"#fd0000",  # 3.00 - 4.00 inches
	"#d40000",  # 4.00 - 5.00 inches
	"#bc0000",  # 5.00 - 6.00 inches
	"#f800fd",  # 6.00 - 8.00 inches
	"#9854c6"  # 8.00 - 10.00 inches
	# "#fdfdfd"   # 10.00+
]
precip_colormap = matplotlib.colors.ListedColormap(nws_precip_colors)

def Mapshow(dims, data, type, para1, para2, tit, unit):

	# Prepare for drawing
	lons = np.arange(dims['minlon'], dims['maxlon']+dims['res']/2, dims['res'])
	lats = np.arange(dims['minlat'], dims['maxlat']+dims['res']/2, dims['res'])
	x, y = np.meshgrid(lons, lats)
	# draw Chile Basemap with lambert projection at normal x, y settings
	m = Basemap(llcrnrlon=dims['minlon'], llcrnrlat=dims['minlat'], urcrnrlon=dims['maxlon'], urcrnrlat=dims['maxlat'], projection='cyl', fix_aspect=True, lat_1=-10, lat_2=10, lon_0=20) # projection='lcc'
	# draw boundaries
	m.drawcoastlines(); m.drawcountries(linewidth=2); m.drawstates()
	m.drawparallels(arange(-20, 30, 20), labels=[1, 0, 0, 0])  # only left ytick
	m.drawmeridians(arange(-10, 60, 20), labels=[0, 0, 0, 1])  # only bottom xtick
	# for  the classified figure
	X, Y = m(x, y)
	if type == 'imshow':
		# im = m.contourf(X, Y, data, cmap=plt.cm.bwr, extend='both')
		plotdata = m.transform_scalar(data, lons, lats, dims['nlon'], dims['nlat'])
		im = m.imshow(plotdata, vmin=para2, vmax=para1, cmap=plt.cm.bwr)
	elif type == 'contour':
		if para1 is not None:
			im = m.contourf(X, Y, data, para1, cmap=plt.cm.bwr, extend='both')
		else:
			im = m.contourf(X, Y, data, cmap=plt.cm.bwr, extend='both')
		cb = m.colorbar(im, pad='3%', ticks=para2)    # cb = m.colorbar(im, location='bottom', pad='16%')
		# The following method will return the zero as a small number close to zero
		# if para2 is not None:
		# 	cb.set_ticks(para2)
		# 	cb.set_ticklabels(para2)

	# map data with lon and lat position
	plt.title(tit, fontsize=20)
	plt.xlabel(unit, fontsize=18, labelpad=15)
	# plt.show()

def Mapshow_basin(data, clevs, cblevs, tit, unit):

	# Prepare for drawing
	# ny, nx = (60, 156)
	lons = np.arange(-72.875, -70., 0.25)
	lats = np.arange(-37.375, -33.75, 0.25)
	x, y = np.meshgrid(lons, lats)
	# draw Chile Basemap with lambert projection at normal x, y settings
	m = Basemap(llcrnrlon=-72.875, llcrnrlat=-37.375, urcrnrlon=-70.125, urcrnrlat=-33.875, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-73) # projection='lcc'
	# draw boundaries
	m.drawcoastlines(); m.drawcountries(linewidth=2); m.drawstates()
	m.drawparallels(arange(-60, -15, 15), labels=[1, 0, 0, 0])  # only left ytick
	m.drawmeridians(arange(-80, -60, 5), labels=[0, 0, 0, 1])  # only bottom xtick
	# for  the classified figure
	# use contourf
	X, Y = m(x, y)

	if clevs == None:
		im = m.contourf(X, Y, data, cmap=precip_colormap, extend='both')
	else:
		im = m.contourf(X, Y, data, clevs, cmap=precip_colormap, extend='both')
	cb = m.colorbar(im, location='bottom', pad='16%')
	if cblevs is not None:
		cb.set_ticks(cblevs)
		cb.set_ticklabels(cblevs)

	# map data with lon and lat position
	plt.title(tit, fontsize=16)
	plt.xlabel(unit, labelpad=20)



def Scatter(data, lons, lats, min, max, cmp, tit, unit, figdir, filename):
	# Prepare for drawing
	# ny, nx = (50, 116)
	# draw Chile Basemap with lambert projection at normal x, y settings
	m = Basemap(llcrnrlon=-78, llcrnrlat=-56, urcrnrlon=-66, urcrnrlat=-17, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-72) # projection='lcc'
	# draw boundaries
	m.drawcoastlines(); m.drawcountries(linewidth=2); m.drawstates()
	m.drawparallels(arange(-60, -15, 15), labels=[1, 0, 0, 0])  # only left ytick
	m.drawmeridians(arange(-80, -60, 5), labels=[0, 0, 0, 1])  # only bottom xtick
	# map data with lon and lat position
	im = m.scatter(lons, lats, 30, marker='o', c=data, vmin=min, vmax=max, latlon=True, cmap=cmp)
	cb = m.colorbar(im, pad='10%')
	plt.title(tit, fontsize=20)
	plt.xlabel(unit, labelpad=50)
	#savefig('%s%s' % (figdir, filename))
	plt.show()

def CateScatter(data, lons, lats, tit, unit, figdir, filename):
	# draw Chile Basemap with lambert projection at normal x, y settings
	m = Basemap(llcrnrlon=-78, llcrnrlat=-56, urcrnrlon=-66, urcrnrlat=-17, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-72) # projection='lcc'
	# draw boundaries
	m.drawcoastlines(); m.drawcountries(linewidth=2); m.drawstates()
	m.drawparallels(arange(-60, -15, 15), labels=[1, 0, 0, 0])  # only left ytick
	m.drawmeridians(arange(-80, -60, 5), labels=[0, 0, 0, 1])  # only bottom xtick
	# map data with lon and lat position
	bins = linspace(0, 100, 6)
	colors = r_[linspace(0.1, 1, 7), linspace(0.1, 1, 7)]
	mymap = plt.get_cmap("Greens")
	my_colors = mymap(colors)
	for i in xrange(0, 5):
		idx = np.where((data>bins[i])& (data<bins[i+1]))
		x = lons[idx[0]]; y = lats[idx[0]]
		im = m.scatter(x, y, 30, marker='o', c=my_colors[i], vmin=min, vmax=max, latlon=True, label=('>'+ str(bins[i]) +'%'))
	plt.legend(scatterpoints=1, loc=2)
	plt.title(tit, fontsize=20)
	plt.xlabel(unit, labelpad=50)
	#savefig('%s%s' % (figdir, filename))
	plt.show()
	plt.clf()

def ScatterShow(data, lons, lats, min, max):
	# Prepare for drawing
	# ny, nx = (50, 116)
	# draw Chile Basemap with lambert projection at normal x, y settings
	# m = Basemap(llcrnrlon=-78, llcrnrlat=-56, urcrnrlon=-66, urcrnrlat=-17, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-72) # projection='lcc'
	m = Basemap(llcrnrlon=-80.875, llcrnrlat=-56., urcrnrlon=-66.125, urcrnrlat=-17, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-73) # projection='lcc'
	# draw boundaries
	# m.drawcoastlines(); m.drawcountries(linewidth=2); m.drawstates()
	# m.drawparallels(arange(-60, -15, 15), labels=[1, 0, 0, 0])  # only left ytick
	# m.drawmeridians(arange(-80, -60, 5), labels=[0, 0, 0, 1])  # only bottom xtick
	# map data with lon and lat position
	cmp = precip_colormap
	im = m.scatter(lons, lats, 20, marker='o', c=data, vmin=min, vmax=max, latlon=True, cmap=cmp)
	# cb = m.colorbar(im, pad='10%')
	# plt.show()
	# plt.clf()

def ScatterShow_basin(data, lons, lats, min, max):
	m = Basemap(llcrnrlon=-72.875, llcrnrlat=-37.375, urcrnrlon=-70.125, urcrnrlat=-33.875, projection='cyl', fix_aspect=False, lat_1=-43, lat_2=-30, lon_0=-73) # projection='lcc'
	cmp = precip_colormap
	im = m.scatter(lons, lats, 80, marker='o', lw=1.2, c=data, vmin=min, vmax=max, latlon=True, cmap=cmp)
