
from PID import PID

import sys
import math
import numpy as np
import random
import copy

import matplotlib.pyplot as plt
import seaborn as sns

class Motor:

	def __init__(self, inertia, damping):
		self.__theta_m = 2*np.pi * 1000
		self.__pressure_m = 150			# MPa
		self.__pressure_coef = [0,0.1,0,0,0,0.9]
		self.__pressure_order = len(self.__pressure_coef) - 1

		self.__inertia= inertia
		self.__damping = damping

		self.__pitch = 4						# mm
		self.__area = np.pi * 6 * 6		# mm^2
		self.__gearRatio = 50

		self.__max_torque = 200		# Nm

		self.__thetas = np.linspace(0,self.__theta_m,11)
		self.__pressures = self.__thetas * 0
		for i in range(0,len(self.__thetas)):
			self.__pressures[i] = self.__calcPressure(self.__thetas[i])

	def __calcPressure(self, theta):
		beta = np.linspace(0,self.__pressure_order,self.__pressure_order+1)
		return self.__pressure_m * sum(self.__pressure_coef * np.power(theta/self.__theta_m, beta))

	def __calcPressureD1(self, theta):
		beta = np.linspace(1,self.__pressure_order,self.__pressure_order)

		pressure_d1_coef = copy.deepcopy(self.__pressure_coef)
		del pressure_d1_coef[0]

		return self.__pressure_m * sum(pressure_d1_coef * np.power(theta/self.__theta_m, beta-1) * beta / self.__theta_m)

	def __calcPressureD2(self, theta):
		beta = np.linspace(2,self.__pressure_order,self.__pressure_order-1)

		pressure_d2_coef = copy.deepcopy(self.__pressure_coef)
		del pressure_d2_coef[0]
		del pressure_d2_coef[0]

		return self.__pressure_m * sum(pressure_d2_coef * np.power(theta/self.__theta_m, beta-2) * beta * (beta-1) / self.__theta_m/self.__theta_m)


	def __calcMCK(self, t, x, dx):
		ndim = 1
		theta = np.interp(x,self.__pressures,self.__thetas)
		dp = self.__calcPressureD1(theta)
		ddp = self.__calcPressureD2(theta)

		M = np.eye(ndim) * self.__inertia / dp
		C = np.eye(ndim) * self.__damping / dp
		K = np.eye(ndim) * 0
		# K = np.eye(ndim) * self.__pitch * self.__area / 2 / np.pi / self.__gearRatio * 1e-3

		return (M,C,K)

	def __calcAdv(self, t, x, dx):

		ndim = 1
		theta = np.interp(x,self.__pressures,self.__thetas)

		dp = self.__calcPressureD1(theta)
		ddp = self.__calcPressureD2(theta)

		A = np.eye(ndim) * ( - self.__inertia * ddp / dp / dp / dp )
		return A*0

	def __calcExciteLimitation(self, t, x, dx, exc):
		Tw = x * self.__pitch * self.__area / (2 * np.pi * self.__gearRatio) * 1e-3

		if exc[0] < -20-Tw[0]:
			exc[0] = -20-Tw[0]
		if exc[0] > 20-Tw[0]:
			exc[0] = 20-Tw[0]

		return exc

	def __stopCriteria(self, t, x, dx):
		return (x > self.__pressure_m * 1.2) or (x<0)

	def __noise(self, ndim):
		y = np.zeros(2*ndim)
		for idim in range(0,2*ndim):
			y[idim] = random.random() * 0.00
		return y


	def __target(self, t):
		y = np.ones(1)
		y[0] = self.__pressure_m # * (1-np.exp(-t/10))

		return y

	def setPIDParameters(self, A):
		self.__PIDParameters = A

	def __calcPIDParameters(self, t, x, dx):

		v = np.array([1,t,x[0],dx[0]])
		kp = np.dot(self.__PIDParameters[0,:], v)
		ki = np.dot(self.__PIDParameters[1,:], v)
		kd = np.dot(self.__PIDParameters[2,:], v)

		return (kp,ki,kd)

	def run(self):
		
		ndim = 1

		p0 = self.__calcPressure(self.__theta_m*0.1)

		pid = PID(dim=ndim)
		pid.setPID(self.__target, self.__calcPIDParameters)
		pid.setSystem(self.__calcMCK, self.__noise)
		pid.setAdvection(self.__calcAdv)
		pid.setExciteLimitation(self.__calcExciteLimitation)
		pid.setStopCriteria(self.__stopCriteria)
		pid.setInitial(p0,0)

		(res, excitations, rs) = pid.solve()
		torques = excitations[:,1] + res[:,1] * self.__pitch * self.__area / (2 * np.pi * self.__gearRatio) * 1e-3

		ax = plt.subplot('111')
		ax.set_xlabel('time(s)')
		ax.set_ylabel('Pressure (MPa)')
		ax.plot(res[:,0], res[:,1], color='red', label=('actual'))
		ax.plot(rs[:,0], rs[:,1], '--', color='red', label=('target'))
		ax.legend(loc='upper right')

		ax2 = ax.twinx()
		ax2.set_ylabel('torque (Nm)')
		ax2.plot(excitations[:,0], torques, '-.', color='black', label='excitation')

		# mng = plt.get_current_fig_manager()
		# mng.window.showMaximized()
		# mng.full_screen_toggle()
		plt.show()
		
		


