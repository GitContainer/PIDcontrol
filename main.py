from PID import PID
from motor import Motor

import numpy as np

A = np.zeros((3,4))
A[0,:] = np.array([2e-4, 0, -0, 0])
A[1,:] = np.array([0, 0, 0, 0])
A[2,:] = np.array([8, 0, 0, 0])

motor = Motor(inertia=0.0025, damping=0.0001)
motor.setPIDParameters(A)
motor.run()



