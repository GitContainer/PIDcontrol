# Rounge-Kutta (4th order) method for ode solving

import numpy as np

class RK4:

	def __init__(self):

		self.__name = "General Rounge-Kutta (4th order) ode solver"
		self.__dfunc = None
		self.__xstep = 0.1

		self.__x = 0
		self.__y = 0


	def setDiffFunction(self, dfunc):
		self.__dfunc = dfunc


	def setXstep(self, step):
		self.__xstep = step


	def initialize(self, xvalue, yvalue):
		self.__x = xvalue
		self.__y = np.array(yvalue)

	def iterate(self, nstep):
		dim = len(self.__y)
		res = np.zeros((nstep+1,dim+1))

		res[0][0] = self.__x
		for i in range(0,dim):
			res[0][1+i] = self.__y[i]

		for istep in range(0,nstep):
			self.iterate_one_step()

			res[istep+1][0] = self.__x
			for i in range(0,dim):
				res[istep+1][1+i] = self.__y[i]

		return res

	def iterate_one_step(self):

		x = self.__x
		y = self.__y
		h = self.__xstep

		k1 = self.__dfunc(x,y)
		k2 = self.__dfunc(x+0.5*h, y+0.5*h*k1)
		k3 = self.__dfunc(x+0.5*h, y+0.5*h*k2)
		k4 = self.__dfunc(x+h,y+h*k3)

		self.__x = x + h
		self.__y = y + (k1+2*k2+2*k3+k4) * h / 6

		return (self.__x, self.__y)

	def setCurrentValue(self, y):
		self.__y = y
