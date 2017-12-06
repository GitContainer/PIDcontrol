from PID import PID

import sys
import math
import numpy as np
import random


def calcMCK(t, x, dx):

	ndim = len(x)

	M = np.eye(ndim)
	C = np.eye(ndim) * 10.0
	K = np.eye(ndim) * 100.0

	M[0][0] = 2 + np.sin(t)
	# M[1][0] = 10 + np.sin(t)

	return (M,C,K)

def noise(ndim):
	y = np.zeros(2*ndim)
	for idim in range(0,2*ndim):
		y[idim] = random.random() * 0.05
	return y


def r(t):
	y = np.ones(1)

	if (int(t/5)%2==0):
		y[0] = 0.7
		# y[1] = 0.2
	else:
		# y[1] = 0.7
		y[0] = 0.2


	# f = 1-np.sin(t)
	# y[0] = f * np.cos(t)
	# y[1] = f * np.sin(t)

	return y

ndim = 1

kp = 500
ki = 200
kd = 100

# kp = np.array([[1,0],[0,1]]) * 50
# ki = np.array([[1,0],[0,0]]) * 200
# kd = np.array([[1,0],[0,1]]) * 10

# kp = np.zeros((ndim,ndim))
# ki = np.zeros((ndim,ndim))
# kd = np.zeros((ndim,ndim))

# f = open(sys.argv[1], 'r')
# kp = float(f.readline())
# ki = float(f.readline())
# kd = float(f.readline())
# f.close()

# print 'PID = (%s, %s, %s)' % (kp, ki, kd)

pid = PID(dim=ndim)
pid.setPID((kp,ki,kd),r)
pid.setSystem(calcMCK, noise)
pid.solve()
# pid.showTrace(0,1)
# pid.showEigenValue()
pid.save('output.xml')

# (steady_state_error, overshoot, delay_time, rise_time, setting_time) = pid.solve()

# print 'Steady state error = %s' % steady_state_error
# print 'Maximum overshoot = %s' % overshoot
# print 'Delay time = %s' % delay_time
# print 'Rise time = %s' % rise_time
# print 'Setting time = %s' % setting_time

# fo = open(sys.argv[2], 'w')
# fo.write('Steady state error = %s\n' % steady_state_error)
# fo.write('Maximum overshoot = %s\n' % overshoot)
# fo.write('Delay time = %s\n' % delay_time)
# fo.write('Rise time = %s\n' % rise_time)
# fo.write('Setting time = %s\n' % setting_time)
# fo.close()
