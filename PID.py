from RK4 import RK4

import numpy as np
import matplotlib.pyplot as plt

class PID:

	def __init__(self, dim):
		self.__name = 'PID core'
		self.__dim = dim
		self.__solver = RK4()

		self.__timestep = 0.02
		self.__PID_IntegralItem = np.zeros((self.__dim))

		self.__PID_param = None
		self.__PID_target = None
		self.__sys_MCK = None


	def setPID(self, param, target):
		self.__PID_param = param
		self.__PID_target = target

	def setMCK(self, func):
		self.__sys_MCK = func

	def __dfunc(self, t, X):

		ndim = self.__dim

		x = X[0:ndim]
		dx = X[ndim:2*ndim]

		(M,C,K) = self.__sys_MCK(t,x,dx)
		invM = np.linalg.inv(M)

		kp = self.__PID_param[0]
		ki = self.__PID_param[1]
		kd = self.__PID_param[2]

		r = self.__PID_target(t)
		dr = (r - self.__PID_target(t-self.__timestep)) / self.__timestep

		ddx = - np.dot(invM, np.dot(K+kp, x)) - np.dot(invM, np.dot(C+kd, dx))
		ddx = ddx + np.dot(invM, np.dot(kp,r)) + np.dot(invM, np.dot(kd,dr))
		ddx = ddx - self.__PID_IntegralItem

		df = np.zeros(2*ndim)
		df[0:ndim] = dx
		df[ndim:2*ndim] = ddx
		
		return df


	def solve(self):

		ndim = self.__dim

		nstep = 1000
		ts = np.zeros(nstep)
		rs = np.zeros((nstep,ndim))
		for i in range(0,nstep):
			ts[i] = self.__timestep*i
			rs[i][:] = self.__PID_target(ts[i])

		t0 = 0

		X0 = np.zeros(2*ndim) 
		X0[ndim:2*ndim] = 1

		res = np.zeros((nstep+1,2*ndim+1))

		res[0][0] = t0
		res[0][1:2*ndim+1] = X0

		self.__solver.setXstep(self.__timestep)
		self.__solver.setDiffFunction(self.__dfunc)
		self.__solver.initialize(t0,X0)
		self.__PID_IntegralItem = np.zeros(ndim)

		for istep in range(0,nstep):
			(t, x) = self.__solver.iterate_one_step()

			res[istep+1][0] = t
			res[istep+1][1:2*ndim+1] = x

			r0 = self.__PID_target(t-self.__timestep)
			r1 = self.__PID_target(t)
			r = (r0+r1)/2

			self.__PID_IntegralItem = self.__PID_IntegralItem + np.dot(self.__PID_param[1], x[0]-r) * self.__timestep


		features = {}
		for idim in range(0,ndim):
			rss = rs[nstep-1][idim]
			steady_state_error = res[nstep-1][1+idim] - rss

			xmax = np.max(res[:,1+idim])
			overshoot = xmax - rss

			setting_time = ts[nstep-1]
			for j in range(0,nstep):
				istep = nstep-1-j
				t = res[istep][0]
				x = res[istep][1+idim]
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
				x = res[istep][1+idim]
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

			features[idim] = (steady_state_error, overshoot, delay_time, rise_time, setting_time)


		colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
		for idim in range(0,ndim):
			ax = plt.subplot('%s1%s'%(ndim,idim+1))
			ax.set_xlabel('time(s)')
			ax.set_ylabel('dim(%s)'%(idim+1))
			ax.plot(res[:,0], res[:,1+idim], color=colors[idim], label=('actual'))
			ax.plot(ts, rs[:,idim], '--', color=colors[idim], label=('target'))
			ax.legend(loc='upper right')


			(steady_state_error, overshoot, delay_time, rise_time, setting_time) = features[idim]
			text =        'Steady state error = %s\n' % steady_state_error
			text = text + 'Maximum overshoot = %s\n' % overshoot
			text = text + 'Delay time = %s\n' % delay_time
			text = text + 'Rise time = %s\n' % rise_time
			text = text + 'Setting time = %s\n' % setting_time
			ax.text(ts[nstep-1] * 0.8, 0, text)

			# ax.annotate('features', xy=(ts[nstep-1], rs[nstep-1][idim]), xytext=(ts[nstep-1], rs[nstep-1][idim]), arrowprops=dict(facecolor='black', shrink=0.1))
		mng = plt.get_current_fig_manager()
		mng.window.showMaximized()
		# mng.full_screen_toggle()
		plt.show()