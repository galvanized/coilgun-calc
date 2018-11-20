from simulate import *
from scipy import optimize as opt
import time

def run(v, verbose=False):
    # fixed
    c = Constants()
    p = Projectile(0.001,0.01)
    g = Coilgun(c, p)
    cap = Capacitor(0.001, 400, 0.01)
    
    #vary
    
    s1w, s2w, s3w, s1l, s2l, s3l, s1d, s2d, s3d = v
    
    s1 = Stage(c, cap, s1w, s1l, s1d)
    s2 = Stage(c, cap, s2w, s2l, s2d)
    s3 = Stage(c, cap, s3w, s3l, s3d)
    
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
        g.step(0.00001, verbose)
        g.simplestaging(verbose)
    
    loss = 0
    loss -= p.v
    
    # encourage using less than 1500 winds total
    loss += max(0, s1w+s2w+s3w - 1500) * 10

    # force all positive
    loss += 1e10 if not allpositive(s1w, s2w, s3w, s1l, s2l, s3l, s1d, s2d, s3d) else 0
    
    # encourage correct ordering
    loss += max(0, s1d - s2d)
    loss += max(0, s2d - s3d)
    
    print('v: {:.1f}   d: {:.1f}    l: {:.0e}    \nv: {}'.format(p.v, p.p, loss, v))
    return loss
    
def allpositive(*l):
    for i in l:
        if i <= 0:
            return False
    return True
    
    

if __name__ == '__main__':
    x0 = np.array([1,1,1,1,1,1,1,1,1])
    b = [(100,1500), (100,1500), (10,1500),
         (0,0.1), (0,0.1), (0,0.1),
         (0,0.01), (0,0.5), (0,1)]
    res = opt.differential_evolution(run, b, init='latinhypercube', popsize=100)
    #res = opt.basinhopping(run, x0)
    print(res.x, res.fun)
    
    tstart = time.time()
    run(res.x, verbose=True)
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

    
