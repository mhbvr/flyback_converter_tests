import numpy as np, matplotlib, sys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','')
def ld(n):
    d=np.genfromtxt(D+f'pwm-{n}.csv',delimiter=',',skip_header=33); return d[:,0],d[:,1],d[:,2]
S=np.load(sys.argv[1]); names=['t','bench','iin','vdd','g','d','s','out','isp','isd','isdrv','isc','pwm','ilp','ism','iss','pdot']
S={n:S[i] for i,n in enumerate(names)}
def edge(t,y,th,rising=True):
    i=np.where((y[:-1]<th)&(y[1:]>=th))[0] if rising else np.where((y[:-1]>=th)&(y[1:]<th))[0]
    return t[i]
# align on drain falling (turn-on) edge
fig,ax=plt.subplots(4,1,figsize=(12,13))
sd=edge(S['t'],S['pwm'],1.65,True)
for k,(n,col,yl) in enumerate([('drain','d','Vds [V]'),('secondary','s','V secondary [V]'),('gate','g','Vgate [V]')]):
    t,p,v=ld(n); md=edge(t,v,3 if n!='secondary' else -20,False) if n!='gate' else edge(t,v,2.5,True)
    t0m=edge(t,p,1.65,True)[0]; t0s=edge(S['t'],S['pwm'],1.65,True)[-3]
    ax[k].plot((t-t0m)*1e6,v,'k',lw=0.8,label='measured')
    ax[k].plot((S['t']-t0s)*1e6,S[col],color='#d1495b',lw=0.9,alpha=0.9,label='ngspice (fitted model)')
    ax[k].set_xlim(-0.5,10.5 if n!='gate' else 4); ax[k].set_ylabel(yl); ax[k].grid(); ax[k].legend(loc='upper right')
ax[2].plot((S['t']-t0s)*1e6,S['vdd'],'b',lw=0.8,label='sim VDD rail'); ax[2].set_ylim(-1,6.5)
ax[2].legend()
ax[3].plot((S['t']-sd[-3])*1e6,S['ism'],'r',label='MOSFET Id (sim)'); ax[3].plot((S['t']-sd[-3])*1e6,S['iss']*10,'g',label='10 x I secondary (sim)'); ax[3].plot((S['t']-sd[-3])*1e6,S['isc'],'b',lw=.7,label='10uF cap current (sim)')
ax[3].set_xlim(-0.5,10.5); ax[3].grid(); ax[3].legend(); ax[3].set_xlabel('time from PWM rising edge [us]'); ax[3].set_ylabel('A')
plt.tight_layout(); plt.savefig(sys.argv[2],dpi=85)
