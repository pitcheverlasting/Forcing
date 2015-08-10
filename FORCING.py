# coding=utf-8
__author__ = 'lpeng'
"""Forcing Preprocess library"""

import numpy as np
import datetime
import pandas as pd
import scipy.optimize

class Data:

	# Initialization
	def __init__(self, grid_data):

		# Read data from the binary file
		# forcing = ('tas', 'dlwrf', 'dswrf', 'shum', 'pres', 'wind', 'prec', 'tmax', 'tmin')
		INPUT = self.Read_Grid_Data(grid_data)

		# Define the incoming grid data variables
		self.Tair = self.Convert_Unit_Temp(INPUT['Tair'])
		self.LWin = self.Convert_Unit_Rad(INPUT['LWin'])
		self.SWin = self.Convert_Unit_Rad(INPUT['SWin'])
		self.SHum = INPUT['SHum']  # (kg kg^-1)
		self.Pres = self.Convert_Unit_Pres(INPUT['Pres'])
		self.Wind = self.Convert_Unit_Wind(INPUT['Wind'])
		self.Prec = INPUT['Prec']  # (mm/d)
		self.Tmax = self.Convert_Unit_Temp(INPUT['Tmax'])
		self.Tmin = self.Convert_Unit_Temp(INPUT['Tmin'])

		# Calculate some variables
		self.Calculate_Rnet()
		self.Calculate_Humidity()  # self.e
		self.Calculate_Saturated_Vapor_Pressure()
		self.Calculate_Slope_Saturation_Vapor_Pressure_Curve()
		self.Calculate_Dewpoint()  # self.Td
		self.Calculate_Gamma()
		self.Calculate_PE_FAO56()


	def Read_Grid_Data(self, grid_data):

		varname = ('Tair', 'LWin', 'SWin', 'SHum', 'Pres', 'Wind', 'Prec', 'Tmax', 'Tmin')
		INPUT = {varname[i]: grid_data[:, i] for i in range(len(varname))}
		# INPUT[] = {grid_data[:, 1]}

		return INPUT

	def Calculate_Humidity(self):
		self.e = self.SHum * self.Pres / 0.662
		return

	def Calculate_Saturated_Vapor_Pressure(self):

		e_tmax = 0.6108 * np.exp((17.27 * self.Tmax) / (237.3 + self.Tmax))
		e_tmin = 0.6108 * np.exp((17.27 * self.Tmin) / (237.3 + self.Tmin))
		self.estar = (e_tmax + e_tmin) / 2

		return

	def Calculate_Slope_Saturation_Vapor_Pressure_Curve(self):

		self.DELTA = 4098 * self.estar / (237.3 + self.Tair) ** 2

		return

	def Calculate_Rnet(self):

		albedo = 0.23
		stefan_b = 4.903e-9  # [MJ K-4 m-2 day-1]
		self.Rn = (1 - albedo) * self.SWin + self.LWin - stefan_b * (self.Tair+273.16)**4

		return

	# Convert unit for DSSAT
	# Kalvin to celcius degree

	def Convert_Unit_Temp(self, input):
		data = input - 273.16
		return data

	# W/m2 to MJ/m2/day
	def Convert_Unit_Rad(self, input):
		data = input / 11.5741
		return data

	# pressure: hpa to kpa

	def Convert_Unit_Pres(self, input):
		data = input / 10**3
		return data

	# Wind: m/s to km/day
	def Convert_Unit_Wind(self, input):
		data = input * 3.6
		return data


	# Shuttleworth Textbook
	def Calculate_Dewpoint(self):
		self.Td = (np.log(self.e) + 0.49299) / (0.0707 - 0.00421 * np.log(self.e))
		return

	def Calculate_Gamma(self):

		cp = 1.013   # Specific heat of moist air at constant pressure [kJ kg-1 C-1]
		lhv = 2.501 - 0.002361 * self.Tair  # Latent heat vapor
		self.gamma = ((cp * self.Pres) / (0.622 * lhv)) * 10 ** (-3)

		return self.gamma

	def Calculate_PE_FAO56(self):

		vpd = self.estar - self.e
		PE_nom = 0.408 * self.DELTA * self.Rn + self.gamma * (900 / (self.Tair+273.16)) * self.Wind * vpd
		PE_denom = self.DELTA + self.gamma * (1 + 0.34 * self.Wind)
		self.PE_fao = PE_nom / PE_denom

		return


	def Calculate_Tmax(self, factor, index): # unit is celcius degree
		def F(tmax):
			e_tmax = 0.6108 * np.exp((17.27 * tmax) / (237.3 + tmax))
			e_tmin = 0.6108 * np.exp((17.27 * self.Tmin[index]) / (237.3 + self.Tmin[index]))
			vpd = (e_tmax + e_tmin)/2 - self.e[index]
			return (0.408 * self.DELTA[index] * self.Rn[index] + self.gamma[index] * (900 / (self.Tair[index]+273.16)) * self.Wind[index] * vpd) / (self.DELTA[index] + self.gamma[index] * (1 + 0.34 * self.Wind[index])) - self.PE_fao[index] * factor
		# init = [20] * len(self.Tmax)
		return scipy.optimize.broyden1(F, 25, f_tol=1e-2)

	def Calculate_Tmin(self, factor, index):
		def F(tmin):
			e_tmax = 0.6108 * np.exp((17.27 * self.Tmax[index]) / (237.3 + self.Tmax[index]))
			e_tmin = 0.6108 * np.exp((17.27 * tmin) / (237.3 + tmin))
			vpd = (e_tmax + e_tmin)/2 - self.e[index]
			return (0.408 * self.DELTA[index] * self.Rn[index] + self.gamma[index] * (900 / (self.Tair[index]+273.16)) * self.Wind[index] * vpd) / (self.DELTA[index] + self.gamma[index] * (1 + 0.34 * self.Wind[index])) - self.PE_fao[index] * factor
		return scipy.optimize.broyden1(F, 15, f_tol=1e-2)

