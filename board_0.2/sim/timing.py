import numpy as np, sys
import os; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','')
def cross(t,y,th,rising):
    i=np.where((y[:-1]<th)&(y[1:]>=th))[0] if rising else np.where((y[:-1]>=th)&(y[1:]<th))[0]
    return t[i]+(th-y[i])/(y[i+1]-y[i])*(t[i+1]-t[i])
def tim(t,p,s):
    out=[]
    for tr in cross(t,p,1.65,True):
        up=cross(t,s,50,True); up=up[up>tr+1e-6]
        if len(up)==0: continue
        dn=cross(t,s,100,False); dn=dn[dn>up[0]]
        if len(dn)==0: continue
        out.append((up[0]-tr, dn[0]-up[0]))
    return np.array(out)
d=np.genfromtxt(D+'pwm-secondary.csv',delimiter=',',skip_header=33)
print('measured: turn-off delay from PWM rise, sec >50V -> <100V duration [us]', tim(d[:,0],d[:,1],d[:,2]).mean(0)*1e6)
for f in sys.argv[1:]:
    S=np.load(f); print(f, tim(S[0],S[12],S[6]).mean(0)*1e6, 'Vout', S[7].mean())
