from PID import PID

import sys
import math
import numpy as np


def calcMCK(t, x, dx):

	ndim = len(x)

	M = np.eye(ndim)
	C = np.eye(ndim) * 1.0
	K = np.eye(ndim) * 20.0

	# M[0][0] = 2
	# M[0][1] = 0.2

	return (M,C,K)


def r(t):
	y = np.ones(3)
	return y

ndim = 3

kp = np.eye(ndim) * 100
ki = np.eye(ndim) * 100
kd = np.eye(ndim) * 100
# f = open(sys.argv[1], 'r')
# kp = float(f.readline())
# ki = float(f.readline())
# kd = float(f.readline())
# f.close()

# print 'PID = (%s, %s, %s)' % (kp, ki, kd)

pid = PID(dim=ndim)
pid.setPID((kp,ki,kd),r)
pid.setMCK(calcMCK)
pid.solve()

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
