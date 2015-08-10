# coding=utf-8
__author__ = 'lpeng'
"""Forcing Preprocess library"""

import numpy as np
import datetime, os
import pandas as pd

class File():
	# Initialization
	def __init__(self, data, dir='/home/water5/lpeng/Projects/CROP/CLIMATE/Weather/', filename="PP01", sy=1948, ey=2012):
		self.data = data
		self.path = dir
		self.filename = filename
		self.styr = sy
		self.edyr = ey

		# self.Rawdata()
		self.WTHwrite()
	def Rawdata(self):
		# set up the first date time column
		dates = pd.date_range((str(1948)+'-01-01'), (str(2012)+'-12-31'), freq='D')
		stdate = pd.date_range((str(1948)+'-01-01'), (str(self.styr-1)+'-12-31'), freq='D')
		eddate = pd.date_range((str(1948)+'-01-01'), (str(self.edyr)+'-12-31'), freq='D')
		outFile = open("%sTEST%4s.txt" %(self.path, self.filename), "w")

		for i in xrange(len(stdate), len(eddate)):
			doy = dates[i].strftime("%y%j")
			# outFile.write("%d  %.1f  %.1f  %.1f  %.1f  %.1f  %.1f\n" % (int(doy), self.data[i, 0], self.data[i, 1], self.data[i, 2], self.data[i, 3], self.data[i, 4], self.data[i, 5]))
			outFile.write("%05d%6.1f%6.1f%6.1f%6.1f%6.1f%6.1f\n" % (int(doy), self.data[i, 0], self.data[i, 1], self.data[i, 2], self.data[i, 3], self.data[i, 4], self.data[i, 5]))
		outFile.close()
		return

	def WTHwrite(self):

		dates = pd.date_range((str(self.styr)+'-01-01'), (str(self.edyr)+'-12-31'), freq='D')
		outFile = open("%sZABA%s.WTH" %(self.path, self.filename), "w")
		# outFile.write("*WEATHER DATA : TEST\n")
		outFile.write("*WEATHER DATA : %s\n" %("ZABA"))
		outFile.write("\n@ INSI      LAT     LONG  ELEV   TAV   AMP REFHT WNDHT\n")
		outFile.write("%6s%9.3f%9.3f%6d%6.1f%6.1f%6.1f%6.1f\n" %("TEST", 19.010, 99.010, 0, 23.6, 3.7, 2, 2))
		outFile.write("@DATE  SRAD  TMAX  TMIN  RAIN  DEWP  WIND\n")
		nt = len(dates)
		for i in xrange(0, nt):
			doy = dates[i].strftime("%y%j")
			outFile.write("%5s%6.1f%6.1f%6.1f%6.1f%6.1f%6.1f\n" % (doy, self.data[i, 0], self.data[i, 1], self.data[i, 2], self.data[i, 3], self.data[i, 4], self.data[i, 5]))
		outFile.close()
		return

