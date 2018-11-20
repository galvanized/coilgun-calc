'''

Simulate and determine optimal design parameters for a coilgun.

'''

from math import *
#import matplotlib.pyplot as plt

u_0 = pi*4e-7 # permeability of free space

class Coilgun():
    def __init__(self, c, p):
        self.c = c # constants
        self.p = p # projectile
        self.stages = []
    
    def step(self, dt):
        current_stage = None
        force = 0
        for s in self.stages:
            
            if s.active:
        
                s.active_time += dt
            
                reactance = 1/4 * s.X_L_1 / s.active_time
                impedance = reactance + s.r + s.cap.r
                
                c.I = s.cap.v / impedance
            
                power = c.I * s.cap.v

                cap_energy = 1/2 * s.cap.c * s.cap.v**2
                new_cap_energy = cap_energy - power*dt
                if new_cap_energy > 0:
                    s.cap.v = sqrt(new_cap_energy*2/s.cap.c)
                else:
                    s.cap.v = 0
                
                projectile_dist = s.p - p.p
                
                # always keep a reasonable distance to prevent force from going to infinity
                g1 = projectile_dist
                g2 = sqrt(s.l**2+c.d_c**2)*copysign(1,projectile_dist)
                g = g1 if abs(g1) > abs(g2) else g2
                
                f = (s.t*c.I)**2*u_0*c.a / (2*g**2*copysign(1,g))
                force += f
                
            else:
                s.active_time = 0
        
        # calculate projectile movement
        a = force / p.m
        p.v += a * dt
        p.p += p.v * dt
        
        
    def addstage(self, stage):
        self.stages.append(stage)
        
    def simplestaging(self):
        # switch on next coil if needed
        switch_next = False
        for s in self.stages:
            if switch_next:
                s.active = True
                print('Engaging!')
                break
            if s.p < p.p and s.active==True:
                # projectile has passed the coil
                switch_next = True
                s.active = False
        

    def fire(self):
        # activates first stage
        self.stages[0].active = True
        
        


class Stage():
    def __init__(self, c, cap, t, l, p, r=0):
        '''
            pass:
            Constants object
            Capacitor object
            coil turns
            coil length
            coil position along barrel
            additional resistance
        '''
        self.c = c
        self.cap = cap
        self.active = False
        self.t = t # coil turns
        self.l = l # coil length (meters)
        self.p = p
        
        self.active_time = 0 # seconds
        
        # coil resistance 
        self.r = c.c * self.t + r
        
        # coil inductance
        self.L = c.u_r * self.t**2 * c.a * 1.26e-6 / self.l
        
        # coil reactance at 1 hz
        self.X_L_1 = 2*pi*self.L
        
        self.I = 0 # instantanious current (amps)
        
class Capacitor():
    def __init__(self, c, v, r):
        '''
            pass:
            constants object
            capacitance
            initial voltage
            internal + line resistance
        '''
        self.c = c
        self.v = v
        self.r = r
        
class Projectile():
    def __init__(self, m, l):
        self.m = m # mass, kg
        self.l = l # length, m
        self.p = 0 # position, m
        self.v = 0 # velocity, m/s
        
        
class Constants():
    def __init__(self):
        self.u_r = 1 # core relative permeability
        self.r_w = 0.001 # wire resistance (ohms per meter)
        self.d_i = 0.01 # coil interior diameter (meters)
        self.d_w = 0.00001 # wire diameter (meters
        self.e = 0.04 # electrical to kinetic efficiency
        self.compute()
        
    def compute(self):
        self.d_c = self.d_i+self.d_w # coil diameter
        self.a = pi*(self.d_c/2)**2 # coil area
        self.c = pi*self.d_c/2 # coil circumference
        
        
if __name__=='__main__':
    c = Constants()
    p = Projectile(0.001,0.01)
    g = Coilgun(c, p)
    cap = Capacitor(0.001, 400, 0.01)
    s1 = Stage(c, cap, 500, 0.05, 0.02)
    s2 = Stage(c, cap, 500, 0.05, 0.07)
    s3 = Stage(c, cap, 500, 0.05, 0.15)
    g.addstage(s1)
    g.addstage(s2)
    g.addstage(s3)
    g.fire()
    
    positions = []
    velocities = []
    voltages = []
    for i in range(100):
        positions.append(p.p)
        velocities.append(p.v)
        voltages.append(cap.v)
        g.step(0.0001)
        g.simplestaging()
    print(list(zip(positions, velocities, voltages)))
