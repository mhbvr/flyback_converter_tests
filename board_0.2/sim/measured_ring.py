import numpy as np
from scipy.optimize import curve_fit
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','')
def ld(n):
    d=np.genfromtxt(D+f'pwm-{n}.csv',delimiter=',',skip_header=33); return d[:,0],d[:,1],d[:,2]
f=lambda t,A,fr,ph,c,tau: A*np.exp(-(t-t[0])/tau)*np.sin(2*np.pi*fr*t+ph)+c
for n,(a,b),g in [('drain',(22.4,26.5),(5,5.6e5,0,4.8,1e-5)),('secondary',(22.6,26.5),(55,5.3e5,0,0,1e-5))]:
    t,p,v=ld(n); m=(t>a*1e-6)&(t<b*1e-6)
    best=None
    for ph in np.linspace(0,2*np.pi,8,endpoint=False):
        try:
            g2=list(g); g2[2]=ph; P,_=curve_fit(f,t[m],v[m],p0=g2,maxfev=20000)
            r=np.std(v[m]-f(t[m],*P))
            if best is None or r<best[1]: best=(P,r)
        except Exception as e: pass
    P,r=best; print(n,'A=%.2f f=%.1f kHz c=%.2f tau=%.2f us resid=%.2f'%(P[0],P[1]/1e3,P[3],P[4]*1e6,r))
