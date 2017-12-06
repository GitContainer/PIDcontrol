from RK4 import RK4

import numpy as np
import matplotlib.pyplot as plt
import  xml.dom.minidom

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
		self.__sys_noise = None

	def setPID(self, param, target):
		self.__PID_param = param
		self.__PID_target = target

	def setSystem(self, mck, noise):
		self.__sys_MCK = mck
		self.__sys_noise = noise

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
		self.__rs = np.zeros((nstep,ndim+1))
		for i in range(0,nstep):
			t = self.__timestep*i
			self.__rs[i][0] = t
			self.__rs[i][1:ndim+1] = self.__PID_target(t)

		t0 = 0

		X0 = np.zeros(2*ndim) 
		X0[ndim:2*ndim] = 1

		self.__res = np.zeros((nstep+1,2*ndim+1))

		self.__res[0][0] = t0
		self.__res[0][1:2*ndim+1] = X0

		self.__solver.setXstep(self.__timestep)
		self.__solver.setDiffFunction(self.__dfunc)
		self.__solver.initialize(t0,X0)
		self.__PID_IntegralItem = np.zeros(ndim)

		for istep in range(0,nstep):
			(t, x) = self.__solver.iterate_one_step()

			x = x + self.__sys_noise(ndim)
			self.__solver.setCurrentValue(x)

			self.__res[istep+1][0] = t
			self.__res[istep+1][1:2*ndim+1] = x

			r0 = self.__PID_target(t-self.__timestep)
			r1 = self.__PID_target(t)
			r = (r0+r1)/2

			self.__PID_IntegralItem = self.__PID_IntegralItem + np.dot(self.__PID_param[1], x[0]-r) * self.__timestep


		self.__features = {}
		for idim in range(0,ndim):
			rss = self.__rs[nstep-1][idim]
			steady_state_error = self.__res[nstep-1][1+idim] - rss

			xmax = np.max(self.__res[:,1+idim])
			overshoot = xmax - rss

			setting_time = self.__rs[nstep-1][0]
			for j in range(0,nstep):
				istep = nstep-1-j
				t = self.__res[istep][0]
				x = self.__res[istep][1+idim]
				setting_time = t
				if np.fabs((x-rss)/rss) >= 0.05:
					break

			t1 = self.__rs[nstep-1][0]
			t5 = self.__rs[nstep-1][0]
			t9 = self.__rs[nstep-1][0]
			t1_found = False
			t5_found = False
			t9_found = False
			for istep in range(0,nstep):
				t = self.__res[istep][0]
				x = self.__res[istep][1+idim]
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

			self.__features[idim] = (steady_state_error, overshoot, delay_time, rise_time, setting_time)


		colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
		for idim in range(0,ndim):
			ax = plt.subplot('%s1%s'%(ndim,idim+1))
			ax.set_xlabel('time(s)')
			ax.set_ylabel('dim(%s)'%(idim+1))
			ax.plot(self.__res[:,0], self.__res[:,1+idim], color=colors[idim], label=('actual'))
			ax.plot(self.__rs[:,0], self.__rs[:,1+idim], '--', color=colors[idim], label=('target'))
			ax.legend(loc='upper right')


			(steady_state_error, overshoot, delay_time, rise_time, setting_time) = self.__features[idim]
			text =        'Steady state error = %s\n' % steady_state_error
			text = text + 'Maximum overshoot = %s\n' % overshoot
			text = text + 'Delay time = %s\n' % delay_time
			text = text + 'Rise time = %s\n' % rise_time
			text = text + 'Setting time = %s\n' % setting_time
			ax.text(self.__rs[nstep-1][0] * 0.8, 0, text)

			# ax.annotate('features', xy=(ts[nstep-1], rs[nstep-1][idim]), xytext=(ts[nstep-1], rs[nstep-1][idim]), arrowprops=dict(facecolor='black', shrink=0.1))
		mng = plt.get_current_fig_manager()
		# mng.window.showMaximized()
		# mng.full_screen_toggle()
		plt.show()


	def showEigenValue(self):

		ndim = self.__dim
		nstep = len(self.__ts)

		lambda_r = np.zeros((nstep,ndim))
		lambda_i = np.zeros((nstep,ndim))

		for istep in range(0,nstep):
			t = self.__ts[istep]

			x = self.__res[istep][1:ndim+1]
			dx = self.__res[istep][ndim+1:2*ndim+1]

			(M,C,K) = self.__sys_MCK(t,x,dx)
			invM = np.linalg.inv(M)

			M1 = np.zeros((ndim,ndim))
			M2 = np.eye(ndim)
			M3 = - np.dot(invM,K)
			M4 = - np.dot(invM,C)

			Mu = np.hstack((M1,M2))
			Mb = np.hstack((M3,M4))
			mat = np.vstack((Mu,Mb))

			a,b = np.linalg.eig(mat)

			for i in range(0,ndim):
				l = a[2*i]
				lambda_r[istep][i] = np.real(l)
				lambda_i[istep][i] = np.fabs(np.imag(l))


		colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta']
		for idim in range(0,ndim):
			ax = plt.subplot('%s1%s'%(ndim,idim+1))
			ax.set_xlabel('time(s)')
			ax.set_ylabel('eigen values for (%s)'%(idim+1))
			ax.plot(self.__ts, lambda_r[:,idim], label='real')
			ax.plot(self.__ts, lambda_i[:,idim], '--', label='imag')
			ax.legend(loc='upper right')
			
		mng = plt.get_current_fig_manager()
		mng.window.showMaximized()
		plt.show()


	def showTrace(self, dim1, dim2):

		plt.plot(self.__res[:,dim1+1], self.__res[:,dim2+1], label='actual')
		plt.plot(self.__rs[:,dim1+1], self.__rs[:,dim2+1], '.', label='target')
		plt.legend(loc='upper right')

		mng = plt.get_current_fig_manager()
		mng.window.showMaximized()
		plt.show()


	def save(self, filename):
		
		ndim = self.__dim

		impl = xml.dom.minidom.getDOMImplementation()
		dom = impl.createDocument(None, 'PID', None)
		root = dom.documentElement

		times = dom.createElement('time-series')
		times.appendChild(dom.createTextNode(','.join(self.__res[:,0].astype(np.str).tolist())))
		root.appendChild(times)

		for idim in range(0,self.__dim):		
			dimension = dom.createElement('dimension')
			dimension.setAttribute('id', '%s'%(idim+1))
			root.appendChild(dimension)

			series = dom.createElement('series')
			series.appendChild(dom.createTextNode(','.join(self.__res[:,1+idim].astype(np.str).tolist())))
			dimension.appendChild(series)

			target = dom.createElement('target')
			target.appendChild(dom.createTextNode(','.join(self.__rs[:,1+idim].astype(np.str).tolist())))
			dimension.appendChild(target)

			features = dom.createElement('features')
			dimension.appendChild(features)

			(steady_state_error, overshoot, delay_time, rise_time, setting_time) = self.__features[idim]

			sse = dom.createElement('steady-state-error')
			sse.appendChild(dom.createTextNode('%s'%steady_state_error))

			mos = dom.createElement('maximum-over-shoot')
			mos.appendChild(dom.createTextNode('%s'%overshoot))

			dt = dom.createElement('delay-time')
			dt.appendChild(dom.createTextNode('%s'%delay_time))

			rt = dom.createElement('rise-time')
			rt.appendChild(dom.createTextNode('%s'%rise_time))

			st = dom.createElement('setting-time')
			st.appendChild(dom.createTextNode('%s'%setting_time))

			features.appendChild(sse)
			features.appendChild(mos)
			features.appendChild(dt)
			features.appendChild(rt)
			features.appendChild(st)


		f = open(filename, 'w')
		dom.writexml(f, addindent='    ', newl='\n')
		f.close()

