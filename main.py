from PID import PID

import sys
import math


def r(t):
	return 1

f = open(sys.argv[1], 'r')
kp = float(f.readline())
ki = float(f.readline())
kd = float(f.readline())
f.close()

print 'PID = (%s, %s, %s)' % (kp, ki, kd)

pid = PID()
pid.setPID((kp,ki,kd),r)
(steady_state_error, overshoot, delay_time, rise_time, setting_time) = pid.solve()

print 'Steady state error = %s' % steady_state_error
print 'Maximum overshoot = %s' % overshoot
print 'Delay time = %s' % delay_time
print 'Rise time = %s' % rise_time
print 'Setting time = %s' % setting_time

fo = open(sys.argv[2], 'w')
fo.write('Steady state error = %s\n' % steady_state_error)
fo.write('Maximum overshoot = %s\n' % overshoot)
fo.write('Delay time = %s\n' % delay_time)
fo.write('Rise time = %s\n' % rise_time)
fo.write('Setting time = %s\n' % setting_time)
fo.close()
