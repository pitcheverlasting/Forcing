# coding=utf-8
__author__ = 'lpeng'
"""PET calculation: FAO Penman-Monteith (FAO-56) potential evapotranspiration, with KC = 1.0"""
"""PET calculation: shuttleworth potential evapotranspiration"""
"""This is function is not finished yet!!!!!!!!!"""


import numpy as np
import datetime
import pandas as pd

class Data:

	# Initialization
	def __init__(self, INPUT):

		# Read data from the binary file
		# forcing = ('tmax', 'tmin', 'rs', 'wind', 'rh')
		# units = ('K', 'K', 'W/m2', 'm/s', 'x100%')

		# Define the incoming grid data variables
		self.Tmax = self.Convert_Unit_Temp(INPUT['Tmax'])
		self.Tmin = self.Convert_Unit_Temp(INPUT['Tmin'])
		self.Rs = self.Convert_Unit_Rad(INPUT['Rs'])
		self.RH = INPUT['RH']
		self.Wind = self.Convert_Unit_Wind(INPUT['wnd10m'])
		self.lat = INPUT['lat']
		self.doy = INPUT['doy']
		self.gslen = INPUT['gslen']
		self.nt = self.Tmax.shape[0]
		self.nx = self.Tmax.shape[1]
		self.ns = self.Tmax.shape[2]

		# Calculate some variables
		self.Calculate_Pressure()
		self.Calculate_Tmean()
		self.Calculate_Saturated_Vapor_Pressure()
		self.Calculate_Humidity()  # self.e
		self.Calculate_Slope_Saturation_Vapor_Pressure_Curve()
		self.Calculate_Rso()
		self.Calculate_Rnet()
		self.Calculate_Gamma()
		self.Penman_FAO56()

	def Calculate_Pressure(self):

		# unit [KPa]
		z1 = 30  #  elevation above sea level
		self.Pres = 101.3 * ((293 - 0.0065 * z1) / 293) ** 5.26

		return


	def Calculate_Tmean(self):

		self.Tmean = (self.Tmax + self.Tmin) / 2.0

		return

	def Calculate_Saturated_Vapor_Pressure(self):

		estar_max = 0.6108 * np.exp((17.27 * self.Tmax) / (237.3 + self.Tmax))
		estar_min = 0.6108 * np.exp((17.27 * self.Tmin) / (237.3 + self.Tmin))
		self.estar = (estar_max + estar_min) / 2

		return

	def Calculate_Humidity(self):

		# mixing = self.SHum / (1 - self.SHum)
		# self.e = mixing * self.Pres / (0.622 + mixing)
		# self.e = self.estar * (self.estar<self.e) + self.e * (self.estar>=self.e)
		self.e = self.estar * self.RH
		self.e = self.estar * (self.RH>1) + self.e * (self.RH<=1)

		return


	def Calculate_Slope_Saturation_Vapor_Pressure_Curve(self):

		# self.DELTA = 4098 * self.estar / (237.3 + self.Tmean) ** 2
		self.DELTA = 4098 * 0.6108 * np.exp((17.27 * self.Tmean) / (237.3 + self.Tmean)) / (237.3 + self.Tmean) ** 2
		return

	def Calculate_Gamma(self):

		# cp = 1.013   # Specific heat of moist air at constant pressure [kJ kg-1 C-1]
		# self.lv = 2.501 - 0.002361 * self.Tmean  # Latent heat vapor
		# self.gamma = ((cp * self.Pres) / (0.622 * self.lv)) * 10 ** (-3)
		self.gamma = 0.000665 * self.Pres
		return


	def Calculate_Rso(self):

		dr = 1 + 0.033 * np.cos(2 * np.pi * self.doy/365.0)  # dr is inverse relative distance Earth-Sun
		d = 0.409 * np.sin((2*np.pi / 365.0) * self.doy - 1.39)   # d is solar declination
		phi =(np.pi/180) * self.lat   # from decimal degree to radians
		omega = np.arccos(-np.tan(phi) * np.tan(d))  # sunset hour angle
		z2 = 30  # set the station elevation above the sea level as 30m
		Gsc = 0.082   # solar constant = 0.082 [MJ m^-2 min^-1]
		# Ra: extraterrestrial radiation for daily period
		Ra = 24 * 60 / np.pi * Gsc*dr*(omega * np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.sin(omega))
		Rso = (0.75 + 2e-5 * z2) * Ra
		## this is a temporary function for Rso
		self.Rso = np.tile(Rso, self.nt/self.gslen)

		return

	def Calculate_Rnet(self):

		# with longwave downward and shortwave downward  [W/m2]
		albedo = 0.23
		# other option: ALBEDO = 0.23-(0.23-SALB)*EXP(-0.75*XHLAI)
		stefan_b = 4.903e-9  # [MJ K-4 m-2 day-1]
		Rns = (1 - albedo) * self.Rs
		## this is a temporary function for cloud fraction
		cloud_fr = np.array([[self.Rs[:, i, j]/ self.Rso for i in xrange(0, self.nx)]  for j in xrange(0, self.ns)])
		cloud_fr = np.swapaxes(cloud_fr, 2, 0)
		Rnl = stefan_b * ((self.Tmax+273.16)**4 + (self.Tmin+273.16)**4) / 2.0 * (0.34-0.14 * np.sqrt(self.e)) * (1.35 * cloud_fr - 0.35)
		self.Rn = Rns - Rnl

		return

	# Convert unit for DSSAT
	# kelvin to degree
	def Convert_Unit_Temp(self, input):
		data = input - 273.16
		return data

	# W/m2 to MJ/m2/day
	def Convert_Unit_Rad(self, input):
		data = input / 11.5741
		return data

	# pressure: pa to kpa
	# def Convert_Unit_Pres(self, input):
	# 	data = input / 1000.0
	# 	return data

	# Wind: m/s
	def Convert_Unit_Wind(self, input):

		zh = 10  # 10 m wind field
		data = (4.87 / (np.log(67.8 * zh - 5.42))) * input

		return data

	# Reference-surface Models
	def Penman_FAO56(self):

		self.vpd = self.estar - self.e
		numerator = self.DELTA + self.gamma * (1 + 0.34 * self.Wind)
		PET_R = 0.408 * self.DELTA * self.Rn / numerator
		PET_A = self.gamma * 900 / (self.Tmean + 273) * self.Wind * self.vpd / numerator
		self.ETo_FAO56 = PET_R + PET_A

		return

	# def Penman(self):
	#
	# 	# Hydrology Book
	# 	# all data are half-hourly time step
	# 	self.vpd = self.estar - self.e
	# 	PET_R = (self.DELTA / (self.DELTA + self.gamma)) * self.Rn / self.lv
	# 	PET_A = (self.gamma / (self.DELTA + self.gamma)) * ((6.43 * (1 + 0.536 * self.Wind) * self.vpd) / self.lv)
	# 	self.PET_Penman = PET_R + PET_A
	#
	# 	return

