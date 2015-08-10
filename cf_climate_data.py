#!/usr/bin/env python
__author__ = 'lpeng'

"""Counterfactual climate datasets forcing"""
##============================================================================================
#	Data: updated version PGF, 1.0 deg, monthly: 1948-2012
#	1. seasonal cycle removal
# 	2. spatial correlation
# 	3. moving window correlation: look at the correlation changes over time
#	4. variables intercorrelation using matrix plot
#	5. variables correlation at different time scales
##============================================================================================

## import library
##---------------
import sys
import time
import os
import glob
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import gc
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, maskoceans
gc.collect()

## start GrADS
##------------
sys.path.insert(0, "/home/water5/lpeng/python/mylib/")
from grads import *
from gradsen import *
gradsen()
ga = GrADS(Bin='/home/latent2/mpan/local/opengrads/Linux/x86_64/grads', Verb=1, Echo=True, Port=False, Window=False, Opts="-c 'q config'")

## import data
##------------
# orgdir = '/home/air2/oldair/raid6/justin/global/forcings/1.0deg/3hourly2daily/'
homedir = '/home/latent2/lpeng/data/forcing/pgf/3hourly2daily/'
forcing = ('tas', 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin', 'vpd')
filename = '_pgf_3hourly2daily_1.0deg_1948-2012.ctl'
# east africa
maskpath = '/home/water5/lpeng/Masks/1.0deg/regions/mask_region_'
masklist = ('eaf','ala', 'amz','aus','cam','cas','cna','grl','med','nas','nec','neu','saf','sah','sahel','sas','sea','ssa','tib','waf','wna','eas','ena','world')

## output path
##------------
figdir = '/home/water5/lpeng/Figure/'

## dimension settings
##-------------------
# glon = 360
# glat = 180
# glon = 60
# glat1 = 60
# glat2 = 120
styr = 1948
edyr = 2012
dates = pd.date_range((str(styr)+'-01-01'), (str(edyr)+'-12-31'), freq='D')

tstep = len(dates)  # tstep = (edyr-styr+1)*12
lstep = (edyr-1948+1) * 12

## turn on sub-seasonal cycle removal
flag_sc = 1

# climcor = np.empty((len(forcing), len(forcing), len(masklist), 2))
# climcor.fill(np.nan)
lat = 80
lon = 40
for i in xrange(0, len(forcing)-1):
	ga("reinit")
	ga("c")
	ctlfile = (homedir + forcing[i] + filename)
	ga.open(ctlfile)
	## data analysis hardcore selection--------------------------------
	# for k in xrange(0, 1):
	# 	maskfile = (maskpath + masklist[k]+'.ctl')
	# 	ga.open(maskfile)
	ga('set x '+str(lon))
	ga('set y '+str(lat))
	ga('set time 01jan'+str(styr)+' 31dec'+str(edyr))
	ga('q dims')
	# export
	data = ga.exp('data')
	print "OK"
	print len(dates)


	ts = Series(data, index=dates)

	# get the lon, lat specific time series
	dayave = ts.groupby(ts.index.dayofyear).mean()
	print dayave
	exit()

	# # for eaf
	# for lon in xrange(0, glon):
	# 	for lat in xrange(glat1-1, glat2):

	# remove the seasonal cycle
	ts_rm = ts - dayave

