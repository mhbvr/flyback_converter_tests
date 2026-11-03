import numpy as np, sys, json
fn=sys.argv[1] if len(sys.argv)>1 else 'out.dat'
P=dict(rlead=0.15,resr=0.45,rw=0.030,rload=31160.,rp=0.015,rs=1.1,rcore=1000.,rcc=0.02)
for a in sys.argv[2:]:
    k,v=a.split('='); v=v.lower(); m={'meg':1e6,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9}
    f=1.0
    for s_,f_ in m.items():
        if v.endswith(s_): v=v[:-len(s_)]; f=f_; break
    P[k]=float(v)*f
d=np.loadtxt(fn); names=['bench','iin','vdd','g','d','s','out','isp','isd','isdrv','isc','pwm','ilp','ism','iss','pdot']
cols={n:d[:,2*i+1] for i,n in enumerate(names)}; t=d[:,0]
pw0=cols['pwm']; ed=t[np.where((pw0[:-1]<1.65)&(pw0[1:]>=1.65))[0]]
t1=ed[-1]; t0=ed[0]; m=(t>=t0)&(t<=t1)
tt=t[m]; c={k:v[m] for k,v in cols.items()}
avg=lambda y: np.trapezoid(y,tt)/(tt[-1]-tt[0])
r={}
r['Pin (bench)']=avg(c['bench']*c['iin'])
r['Iin avg']=avg(c['iin'])
r['lead I2R']=P['rlead']*avg(c['iin']**2)
r['10uF ESR I2R']=P['resr']*avg(c['isc']**2)
r['driver (MCP1407 + gate charge)']=avg(c['vdd']*c['isdrv'])
r['perfboard wiring I2R']=P['rw']*avg(c['isp']**2)
r['primary DCR']=P['rp']*avg(c['ilp']**2)
r['core-loss resistor']=avg((c['pdot']-c['d'])**2)/P['rcore']
r['MOSFET (cond+switch+Coss)']=avg(c['d']*c['ism'])
r['secondary DCR']=P['rs']*avg(c['iss']**2)
r['diode']=avg((c['s']-c['out'])*c['isd'])
r['Pout (into Cout+R)']=avg(c['out']*c['isd'])
r['other (leakage damping, ceramics, probes)']=r['Pin (bench)']-r['Pout (into Cout+R)']-sum(v for k,v in r.items() if k not in ('Pin (bench)','Iin avg','Pout (into Cout+R)'))
r['Vout']=avg(c['out'])
r['Vout steady (sqrt(P*R))']=np.sqrt(r['Pout (into Cout+R)']*P['rload'])
r['Iout mA']=r['Vout steady (sqrt(P*R))']/P['rload']*1e3
r['eff']=r['Pout (into Cout+R)']/r['Pin (bench)']
r['Vds max']=c['d'].max(); r['diode Vrev max']=(c['out']-c['s']).max()
r['Ipk primary']=c['ism'].max(); r['Irms primary']=np.sqrt(avg(c['isp']**2))
r['vdd min/max']=(c['vdd'].min(),c['vdd'].max())
r['gate min during on']=c['g'][(c['pwm']>2)].min() if 1 else 0
r['drain at turn-on']=None
for k,v in r.items(): print(f'{k:32s} {v}')
np.save(fn+'.npy',np.vstack([tt]+[c[n] for n in names]))
# gate (=VDD seen by driver vs MOSFET source) right before turn-off and 0.5us after turn-on
tp=tt; pw=c['pwm']
ri=np.where((pw[:-1]<1.65)&(pw[1:]>=1.65))[0]; fi=np.where((pw[:-1]>=1.65)&(pw[1:]<1.65))[0]
g_end=np.mean([np.interp(tp[i]+60e-9,tp,c['g']) for i in fi])
g_st=np.mean([np.mean(c['g'][(tp>tp[i]+0.6e-6)&(tp<tp[i]+1.0e-6)]) for i in ri if tp[i]+1e-6<tp[-1]])
print(f'{"gate 0.6-1us after on / at end":32s} {g_st:.2f} {g_end:.2f}   (measured ~4.85 / ~4.0)')
sec=c['s']; 
sec_st=np.mean([np.mean(sec[(tp>tp[i]+0.4e-6)&(tp<tp[i]+0.8e-6)]) for i in ri if tp[i]+3.3e-6<tp[-1]])
sec_en=np.mean([np.mean(sec[(tp>tp[i]+2.8e-6)&(tp<tp[i]+3.2e-6)]) for i in ri if tp[i]+3.3e-6<tp[-1]])
print(f'{"sec on-state start/end":32s} {sec_st:.2f} {sec_en:.2f}   (measured -48.65 / -41.82)')
