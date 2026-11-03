import numpy as np, sys
from scipy.optimize import curve_fit
f=lambda t,A,fr,ph,c,tau: A*np.exp(-(t-t[0])/tau)*np.sin(2*np.pi*fr*t+ph)+c
for fn in sys.argv[1:]:
    S=np.load(fn); t=S[0]; v=S[5]; p=S[12]
    r=np.where((p[:-1]<1.65)&(p[1:]>=1.65))[0]; tr=t[r[-2]]
    # measured window: 22.4-26.5us in capture where PWM rose at 16.608 -> 5.79..9.89us after PWM rise
    m=(t>tr+5.8e-6)&(t<tr+9.85e-6); best=None
    for ph in np.linspace(0,6.28,8,endpoint=False):
        try:
            P,_=curve_fit(f,t[m],v[m],p0=[5,5.6e5,ph,4.8,1e-5],maxfev=20000); r_=np.std(v[m]-f(t[m],*P))
            if best is None or r_<best[1]: best=(P,r_)
        except: pass
    P=best[0]; print(fn,'A=%.2f f=%.1f kHz c=%.2f tau=%.2f us; Vds at turn-on %.2f'%(P[0],P[1]/1e3,P[3],P[4]*1e6, np.interp(tr+0.09e-6,t,v)))
