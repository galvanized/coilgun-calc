'''

Simulate and determine optimal design parameters for a coilgun.

'''

from math import *
import numpy as np

#import matplotlib.pyplot as plt

u_0 = pi*4e-7 # permeability of free space

class Coilgun():
    def __init__(self, c, p):
        self.c = c # constants
        self.p = p # projectile
        self.t = 0
        self.stages = []
    
    def step(self, dt, verbose=False):
        current_stage = None
        force = 0
        self.t += dt
        for s in self.stages:
            
            if s.active:
        
                s.active_time += dt
            
                reactance = 1/4 * s.X_L_1 / s.active_time
                impedance = reactance + s.r + s.cap.r
                
                s.I = s.cap.v / impedance
            
                power = s.I * s.cap.v

                cap_energy = 1/2 * s.cap.c * s.cap.v**2
                new_cap_energy = cap_energy - power*dt
                if new_cap_energy > 0:
                    s.cap.v = sqrt(new_cap_energy*2/s.cap.c)
                else:
                    s.cap.v = 0
                
                projectile_dist = s.p - self.p.p
                
                # always keep a reasonable distance to prevent force from going to infinity
                g1 = projectile_dist
                g2 = sqrt(s.l**2+self.c.d_c**2)*copysign(1,projectile_dist)
                g = g1 if abs(g1) > abs(g2) else g2
                
                f = (s.t*s.I)**2 * u_0 * self.c.a / (2*g**2*copysign(1,g))
                force += f
                
            else:
                s.active_time = 0
        
        # calculate projectile movement
        a = force / self.p.m * self.c.fm
        self.p.v += a * dt
        self.p.p += self.p.v * dt
        
        
    def addstage(self, stage):
        self.stages.append(stage)
        
    def simplestaging(self, verbose=False):
        # switch on next coil if needed
        switch_next = False
        for s in self.stages:
            if switch_next:
                s.active = True
                break
            if s.p < self.p.p and s.active==True:
                # projectile has passed the coil
                switch_next = True
                s.active = False
                if verbose:
                        print('Staging. t: {:0.6f} vel: {:0.2f} pos: {:0.2f} vol: {:0.1f}'.format(
                                self.t, self.p.v, self.p.p, s.cap.v))
                                
    def tripwirestaging(self, positions, verbose=False):
        stage_positions = [s.p for s in self.stages]
        p = self.p.p
        for i, (sp, tp) in enumerate(zip(stage_positions, positions)):
            if tp <= p < sp:
                self.stages[i].active = True
            else:
                if self.stages[i].active and verbose:
                    print('Staging. t: {:0.6f} vel: {:0.2f} pos: {:0.2f} vol: {:0.1f}'.format(
                            self.t, self.p.v, self.p.p, self.stages[i].cap.v))
                self.stages[i].active = False
        
            
        

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
        self.fm = 1 # force multiplier
        self.e = 0.04 # electrical to kinetic efficiency
        
        self.stages = 5
        self.init_v = 400 # voltage on capacitors
        self.total_c = 0.001 # capacitance total
        
        self.windlimit = 1800 # sum of all coils' winding numbers
        
        self.compute_time = 0.025 # seconds
        self.compute_steps = 2000
        
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
    s2 = Stage(c, cap, 300, 0.05, 0.07)
    s3 = Stage(c, cap, 200, 0.05, 0.15)
    g.addstage(s1)
    g.addstage(s2)
    g.addstage(s3)
    g.fire()
    
    positions = []
    velocities = []
    voltages = []
    for i in range(10000):
        positions.append(p.p)
        velocities.append(p.v)
        voltages.append(cap.v)
        g.step(0.0001)
        g.tripwirestaging([-1,0.05, 0.1], verbose=True)
    #print(list(zip(positions, velocities, voltages)))
