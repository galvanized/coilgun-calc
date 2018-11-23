from simulate import *
from scipy import optimize as opt
import time

def run(v, verbose=False, nodat=False):
    c = Constants()
    # fixed
    windlimit = c.windlimit
    capacitance = c.total_c
    stagecaps = False
    
    
    c = Constants()
    p = Projectile(0.001,0.01)
    g = Coilgun(c, p)
    cap = Capacitor(capacitance, c.init_v, 0.01)
    
    for s in range(c.stages):
        s = Stage(c, cap, v[2*s], 0.005, v[2*s+1])
        g.addstage(s)
    
    g.fire()
    
    loss = 0
    
    # encourage using less than 1500 winds total
    loss += max(0, sum(v[::2]) - windlimit) * 10

    # force all positive
    loss += 1e10 if not allpositive(*v) else 0
    
    # encourage correct ordering
    pos = v[1::2]
    for i in range(len(pos[:-1])):
        if pos[i] > pos[i+1]:
            loss += (pos[i] - pos[i+1])*10
            
    if loss == 0:
    
        positions = []
        velocities = []
        voltages = []
        compute_dt = c.compute_time / c.compute_steps
        for i in range(c.compute_steps):
            positions.append(p.p)
            velocities.append(p.v)
            voltages.append(cap)
            g.step(compute_dt, verbose)
            g.simplestaging(verbose)
        
        
        loss -= p.v
    
    
    
    if not nodat:
        print('v: {:.1f}   d: {:.1f}    l: {:.0e}    \nv: {}'.format(p.v, p.p, loss, v))
    return loss
    
def allpositive(*l):
    for i in l:
        if i <= 0:
            return False
    return True
    
    
def fmt_mm(v):
    return '{:5.1f} mm'.format(v*1000)
    
def fmt_t(t):
    return '{} turns'.format(int(round(t)))
    

if __name__ == '__main__':
    c = Constants()
    windlimit = c.windlimit
    
    indv = [(1,windlimit), (1e-6, 1)]
    
    b = indv * c.stages
         
    res = opt.differential_evolution(run, b, init='latinhypercube', popsize=2)
    print(res.x, res.fun)
    
    tstart = time.time()
    run(res.x, verbose=True, nodat=True)
    for i in range(c.stages):
        print(fmt_mm(res.x[i*2+1])+'\t'+fmt_t(res.x[i*2]))
        
    print('sim speed: {:0.2f}hz'.format(1/(time.time()-tstart)))
    
    '''
    
       - Evolution Results -
    
    [1.19829036e+01 2.97201836e+02 1.04675559e+03 2.24365031e-03
    5.36914253e-01 5.14889692e-01 6.07346246e-03 4.38773562e-01
    2.46054835e-01] -248.5989029523465
    11 turns, 297 turns, 1046 turns
    2 mm, 537mm, 515 mm coil length
    6mm, 439mm, 246mm position
    
    [3.76341624e+02 2.82838258e+02 1.00002925e+02 6.15699015e-03
    5.73361067e-03 4.62033692e-03 2.53609017e-03 9.05201919e-02
    2.73189560e-01] -272.56152824080453
    376 turns, 282 turns, 100 turns
    6mm, 6mm, 5mm
    2.5mm, 90mm, 273mm
    
    [2.80201084e+02 1.52516033e+02 2.51060226e+02 5.63702433e-03
    4.71957950e-03 6.28752304e-03 9.22666964e-03 1.10097723e-01
    3.32461181e-01] -242.4735911535048
    
    
    Staging. v: 90.68
    Staging. v: 175.25
    Staging. v: 272.56
    v: 2.73e+02   d: 5.42e+01    l: -2.73e+02    
    v: [3.70261077e+02 2.85159801e+02 1.00012423e+02 6.11693720e-03
     5.75241802e-03 4.62044783e-03 4.24030714e-03 9.36592727e-02
     2.67409971e-01]
     
     370 turns, 285 turns, 100 turns
     6mm, 6mm, 5mm
     4mm, 93mm, 267mm
     
     
    Staging. t: 0.000820 vel: 36.28 pos: 0.01 vol: 369.2
    Staging. t: 0.002890 vel: 66.67 pos: 0.09 vol: 322.1
    Staging. t: 0.009040 vel: 84.15 pos: 0.51 vol: 238.2
    v: 84.2   d: 8.2    l: -8e+01    
    v: [2.62554409e+02 4.61911043e+02 7.75402255e+02 9.97447123e-03
     9.34788315e-02 5.09050559e-01]
    sim speed: 11.02hz


    popsize 20
    Staging. t: 0.000980 vel: 32.29 pos: 0.01 vol: 375.5
    Staging. t: 0.004410 vel: 65.45 pos: 0.13 vol: 311.3
    Staging. t: 0.006320 vel: 80.89 pos: 0.26 vol: 242.5
    v: 80.9   d: 7.8    l: -8e+01    
    v: [4.21092747e+02 7.16402417e+02 3.26255858e+02 9.90732152e-03
     1.33009750e-01 2.61421267e-01]
    sim speed: 11.47hz
    
    421, 716, 326 turns
    9.9mm, 133mm, 261mm
    
    
    popsize 100
    Staging. t: 0.001000 vel: 31.90 pos: 0.01 vol: 376.7
    Staging. t: 0.003530 vel: 64.14 pos: 0.10 vol: 319.6
    Staging. t: 0.006030 vel: 80.82 pos: 0.27 vol: 251.8
    v: 80.8   d: 7.9    l: -8e+01    
    v: [4.43369146e+02 5.79061178e+02 4.41296514e+02 9.97662763e-03
     1.01236184e-01 2.65544806e-01]
    sim speed: 11.43hz
    
    443, 579, 441 turns
    10mm, 101mm, 265mm
    
    Staging. t: 0.000950 vel: 32.89 pos: 0.01 vol: 373.6
    Staging. t: 0.004190 vel: 65.11 pos: 0.13 vol: 315.0
    Staging. t: 0.006390 vel: 81.00 pos: 0.28 vol: 243.0
    v: 81.0   d: 7.9    l: -8e+01    
    v: [3.88535838e+02 7.22938020e+02 3.65438071e+02 9.94065579e-03
     1.27928047e-01 2.74936279e-01]
    sim speed: 11.42hz
    
    
    1.2 mF, 0.3 fm, popsize 10
    Staging. t: 0.001460 vel: 20.34 pos: 0.01 vol: 372.6
    Staging. t: 0.005560 vel: 38.72 pos: 0.10 vol: 312.2
    Staging. t: 0.008220 vel: 47.72 pos: 0.21 vol: 250.6
    v: 47.7   d: 4.6    l: -5e+01    
    v: [4.47527127e+02 6.70123512e+02 3.70766148e+02 9.84701394e-03
     1.03281730e-01 2.09379745e-01]
    sim speed: 5.36hz
    448 turns, 670 turns, 370 turns
    
    1.2mF, 0.8fm, popsize 1, windlimit 2000
    Staging. t: 0.000840 vel: 31.85 pos: 0.01 vol: 371.7
    Staging. t: 0.001640 vel: 56.77 pos: 0.04 vol: 322.5
    Staging. t: 0.007460 vel: 74.65 pos: 0.38 vol: 264.9
    8.9 mm 253.0 turns
    39.3 mm 154.0 turns
    375.9 mm 880.0 turns
    sim speed: 10.41hz
    
    
    different caps
    Staging. t: 0.000720 vel: 22.95 pos: 0.01 vol: 299.2
    Staging. t: 0.011180 vel: 23.68 pos: 0.25 vol: 9.6
    Staging. t: 0.012070 vel: 45.54 pos: 0.28 vol: 251.7
    5.9 mm	204 turns
    250.2 mm	425 turns
    277.3 mm	183 turns
    sim speed: 9.02hz
    
    
    shared cap
    Staging. t: 0.000980 vel: 31.15 pos: 0.01 vol: 374.2
    Staging. t: 0.004130 vel: 60.41 pos: 0.12 vol: 324.9
    Staging. t: 0.006830 vel: 76.35 pos: 0.29 vol: 263.8
      9.8 mm	353 turns
    118.6 mm	686 turns
    285.7 mm	447 turns
    
    
    four coils, shared cap
    Staging. t: 0.002600 vel: 54.58 pos: 0.03 vol: 344.4
    Staging. t: 0.007500 vel: 74.90 pos: 0.31 vol: 246.1
    Staging. t: 0.011800 vel: 80.04 pos: 0.63 vol: 116.6
    Staging. t: 0.011900 vel: 80.04 pos: 0.64 vol: 85.9
     28.2 mm	556 turns
    302.2 mm	578 turns
    625.5 mm	273 turns
    415.3 mm	20 turns
    
    four coils, shared cap
    Staging. t: 0.001845 vel: 47.64 pos: 0.02 vol: 355.7
    Staging. t: 0.004710 vel: 68.47 pos: 0.16 vol: 310.2
    Staging. t: 0.005970 vel: 80.45 pos: 0.25 vol: 211.5
    Staging. t: 0.007095 vel: 85.61 pos: 0.34 vol: 154.9
     21.2 mm	457 turns
    164.1 mm	639 turns
    252.3 mm	134 turns
    344.1 mm	139 turns
    
    
    80% force multiplier, 5 stages
    Staging. t: 0.002462 vel: 48.08 pos: 0.03 vol: 360.8
    Staging. t: 0.004250 vel: 67.00 pos: 0.12 vol: 327.3
    Staging. t: 0.005375 vel: 79.96 pos: 0.19 vol: 288.2
    Staging. t: 0.006500 vel: 89.55 pos: 0.29 vol: 239.3
    Staging. t: 0.007225 vel: 95.28 pos: 0.35 vol: 191.6
     25.3 mm	665 turns
    115.5 mm	501 turns
    193.0 mm	264 turns
    284.6 mm	203 turns
    350.9 mm	115 turns
    
    30% force multiplier, 5 stages
    Staging. t: 0.002325 vel: 27.02 pos: 0.02 vol: 359.4
    Staging. t: 0.004225 vel: 38.55 pos: 0.07 vol: 322.0
    Staging. t: 0.005538 vel: 46.35 pos: 0.13 vol: 277.5
    Staging. t: 0.006863 vel: 51.86 pos: 0.19 vol: 218.4
    Staging. t: 0.008413 vel: 55.06 pos: 0.27 vol: 166.2
     17.2 mm	613 turns
     72.6 mm	492 turns
    124.9 mm	277 turns
    187.8 mm	199 turns
    269.1 mm	211 turns
    
    100% force multiplier, 5 stages
    Staging. t: 0.002050 vel: 55.05 pos: 0.03 vol: 355.0
    Staging. t: 0.004000 vel: 77.09 pos: 0.14 vol: 310.1
    Staging. t: 0.005813 vel: 91.02 pos: 0.28 vol: 267.0
    Staging. t: 0.008888 vel: 100.32 pos: 0.56 vol: 191.8
    Staging. t: 0.010125 vel: 104.07 pos: 0.69 vol: 120.2
     24.8 mm	502 turns
    137.7 mm	438 turns
    279.8 mm	380 turns
    561.3 mm	362 turns
    686.8 mm	112 turns








    
    
    
        - Basinhopping Results - 
        
    Staging. v: 93.73
    Staging. v: 93.73
    Staging. v: 93.73
    v: 93.7   d: 18.7    l: -9e+01    
    v: [4.87411451e+01 8.37356899e-02 1.38518280e+00 5.81929955e-04
     1.66265722e+00 9.30610949e-01 5.30454067e-03 1.07384112e+00
     1.78684183e+00]
     487 turns
     .5mm coil
     5mm distance



    '''

    
