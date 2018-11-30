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
    

    
