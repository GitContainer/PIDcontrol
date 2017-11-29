from RK4 import RK4

import numpy as np
import matplotlib.pyplot as plt

class PID:

	def __init__(self):
		self.__name = 'PID core'
		self.__solver = RK4()

		self.__timestep = 0.02
		self.__PID_IntegralItem = 0


	def setPID(self, param, target):
		self.__PID_param = param
		self.__PID_target = target

	def __calcMCK(self, t, x, dx):

		M = 1.0
		C = 1.0
		K = 20.0

		return (M,C,K)

	def __dfunc(self, t, X):

		(M,C,K) = self.__calcMCK(t,X[0],X[1])
		kp = self.__PID_param[0]
		ki = self.__PID_param[1]
		kd = self.__PID_param[2]


		r = self.__PID_target(t)
		dr = (r - self.__PID_target(t-self.__timestep)) / self.__timestep

		df = np.zeros(2)
		df[0] = X[1]
		df[1] = - (K+kp)/M*X[0] - (C+kd)/M*X[1]
		df[1] = df[1] + kp*r + kd*dr
		df[1] = df[1] - self.__PID_IntegralItem
		
		return df


	def solve(self):

		nstep = 1000
		ts = np.zeros(nstep)
		rs = np.zeros(nstep)
		for i in range(0,nstep):
			ts[i] = self.__timestep*i
			rs[i] = self.__PID_target(ts[i])


		t0 = 0
		x0 = 0
		dx0 = 1


		dim = 2
		res = np.zeros((nstep+1,dim+1))

		res[0][0] = t0
		res[0][1] = x0
		res[0][2] = dx0


		self.__solver.setXstep(self.__timestep)
		self.__solver.setDiffFunction(self.__dfunc)
		self.__solver.initialize(t0,[x0,dx0])
		self.__PID_IntegralItem = 0

		for istep in range(0,nstep):
			(t, x) = self.__solver.iterate_one_step()

			res[istep+1][0] = t
			res[istep+1][1] = x[0]
			res[istep+1][2] = x[1]

			r0 = self.__PID_target(t-self.__timestep)
			r1 = self.__PID_target(t)
			r = (r0+r1)/2

			self.__PID_IntegralItem = self.__PID_IntegralItem + self.__PID_param[1] * (x[0]-r) * self.__timestep

		# plt.plot(res[:,0], res[:,1], ts, rs)
		# plt.show()

		rss = rs[nstep-1]
		steady_state_error = res[nstep-1][1] - rss

		xmax = np.max(res[:,1])
		overshoot = xmax - rss

		setting_time = ts[nstep-1]
		for j in range(0,nstep):
			istep = nstep-1-j
			t = res[istep][0]
			x = res[istep][1]
			setting_time = t
			if np.fabs((x-rss)/rss) >= 0.05:
				break

		t1 = ts[nstep-1]
		t5 = ts[nstep-1]
		t9 = ts[nstep-1]
		t1_found = False
		t5_found = False
		t9_found = False
		for istep in range(0,nstep):
			t = res[istep][0]
			x = res[istep][1]
			ratio = np.fabs(x) / np.fabs(rss)

			if not t1_found and ratio>0.1:
				t1 = t
				t1_found = True
			if not t5_found and ratio>0.5:
				t5 = t
				t5_found = True
			if not t9_found and ratio>0.9:
				t9 = t
				t9_found = True

		delay_time = t5
		rise_time = t9 - t1

		return (steady_state_error, overshoot, delay_time, rise_time, setting_time)