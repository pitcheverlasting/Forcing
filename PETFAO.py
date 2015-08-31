# coding=utf-8
__author__ = 'lpeng'
"""PET calculation: FAO Penman-Monteith (FAO-56) potential evapotranspiration, with KC = 1.0"""
"""This is function is not finished yet!!!!!!!!!"""
import numpy as np
import datetime
import pandas as pd

class Data:

	# Initialization
	def __init__(self, grid_data):

		# Read data from the binary file
		# forcing = ('tmax', 'tmin', 'rs', 'wind', 'rh')
		# units = ('K', 'K', 'W/m2', 'm/s', 'x100%')
		INPUT = self.Read_Grid_Data(grid_data)

		# Define the incoming grid data variables
		self.Tmax = self.Convert_Unit_Temp(INPUT['Tmax'])
		self.Tmin = self.Convert_Unit_Temp(INPUT['Tmin'])
		self.Rs = self.Convert_Unit_Rad(INPUT['Rs'])
		self.RH = self.Convert_Unit_Shum(INPUT['RH'])  # (kg kg^-1)
		self.Pres = self.Convert_Unit_Pres(INPUT['Pres'])
		self.Wind = self.Convert_Unit_Wind(INPUT['Wind'])

		# Calculate some variables
		self.Calculate_Rnet()
		self.Calculate_Saturated_Vapor_Pressure()
		self.Calculate_Humidity()  # self.e
		self.Calculate_Slope_Saturation_Vapor_Pressure_Curve()
		self.Calculate_Gamma()
		self.Penman()


	def Read_Grid_Data(self, grid_data):

		# varname = ('LWin', 'SWin', 'Tair', 'Wind', 'Pres', 'SHum')
		varname = ('LWn', 'SWn', 'Tair', 'Wind', 'Pres', 'SHum')
		INPUT = {varname[i]: grid_data[i, :, :] for i in range(0, len(varname))}
		# print INPUT
		# INPUT[] = {grid_data[:, 1]}

		return INPUT

	def Calculate_Saturated_Vapor_Pressure(self):

		self.estar = 0.6108 * np.exp((17.27 * self.Tair) / (237.3 + self.Tair))

		return

	def Calculate_Humidity(self):

		mixing = self.SHum / (1 - self.SHum)
		self.e = mixing * self.Pres / (0.622 + mixing)
		self.e = self.estar * (self.estar<self.e) + self.e * (self.estar>=self.e)

		return


	def Calculate_Slope_Saturation_Vapor_Pressure_Curve(self):

		self.DELTA = 4098 * self.estar / (237.3 + self.Tmean) ** 2

		return

	def Calculate_Tmean(self):

		self.Tmean = (self.Tmax + self.Tmin) / 2.0

	def Calculate_Rnet(self):

		# with longwave downward and shortwave downward  [W/m2]
		albedo = 0.23
		# other option: ALBEDO = 0.23-(0.23-SALB)*EXP(-0.75*XHLAI)
		stefan_b = 4.903e-9  # [MJ K-4 m-2 day-1]
		((self.Tmax+273.16)**4 + (self.Tmin+273.16)**4) / 2.0
		# self.Rn = (1 - albedo) * self.SWin + self.LWin - stefan_b * (self.Tair+273.16)**4

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
	def Convert_Unit_Pres(self, input):
		data = input / 1000.0
		return data

	# Wind: m/s
	def Convert_Unit_Wind(self, input):
		data = input
		return data

	def Convert_Unit_Shum(self, input):
		data = input
		return data

	def Calculate_Gamma(self):

		cp = 1.013   # Specific heat of moist air at constant pressure [kJ kg-1 C-1]
		self.lv = 2.501 - 0.002361 * self.Tair  # Latent heat vapor
		self.gamma = ((cp * self.Pres) / (0.622 * self.lv)) * 10 ** (-3)

		return self.gamma

	# Reference-surface Models
	def Penman(self):

		# Hydrology Book
		# all data are half-hourly time step
		self.vpd = self.estar - self.e
		PET_R = (self.DELTA / (self.DELTA + self.gamma)) * self.Rn / self.lv
		PET_A = (self.gamma / (self.DELTA + self.gamma)) * ((6.43 * (1 + 0.536 * self.Wind) * self.vpd) / self.lv)
		self.PET_Penman = PET_R + PET_A

		return

