'''

Simulate and determine optimal design parameters for a coilgun.

'''

from math import *

class Coilgun():
    
    def step(self, dt):
        pass


class Stage():
    def __init__(self, c, t, l):
        '''
            pass:
            Constants object
            coil turns
            coil length
        '''
        self.t = t # coil turns
        self.l = l # coil length (meters)
        
        # coil resistance 
        self.r = c.c * self.t
        
        # coil inductance
        self.L = c.u_r * self.t**2 * c.a * 1.26e-6 / self.l
        
        # coil reactance at 1 hz
        self.X_L_1 = 2*pi*self.L
        
class Capacitor():
    def __init__(self, c, C, v):
        '''
            pass:
            constants object
            capacitance
            initial voltage
        '''
        self.C = C
        self.v = v
        
        
class Constants():
    def __init__(self):
        self.u_r = 1 # core relative permeability
        self.r_w = 0.001 # wire resistance (ohms per meter)
        self.d_i = 0.01 # coil interior diameter (meters)
        self.d_w = 0.00001 # wire diameter (meters)
        self.compute()
        
    def compute(self):
        self.d_c = self.d_i+self.d_w # coil diameter
        self.a = pi*(self.d_c/2)**2 # coil area
        self.c = pi*self.d_c/2 # coil circumference
        
        
if __name__=='__main__':
    c = Constants()
    s1 = Stage(c, 500, 0.01)
    print(s1.L, s1.r, s1.X_L_1)
        
