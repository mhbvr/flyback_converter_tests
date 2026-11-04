# Board 0.3 design calculations (formulas of DESIGN.md, no circuit simulation). Run: python3 calc.py
import math
pi=math.pi
Vo=170.; Vf=1.0; n=10.; f=100e3; T=1/f; Lp=10e-6; Vm=0.6; Vv=0.7; C=2.2e-6
eta=0.85
Vin_min,Vin_nom,Vin_max=4.5,5.0,5.5
Io_max=15e-3
Vor=(Vo+Vf)/n
print('Vor',Vor)
Po=Vo*Io_max; Pin=Po/eta; E=Pin/f
for L in (9e-6,10e-6,11e-6):
    Ipk=math.sqrt(2*E/L); ton=L*Ipk/Vin_min; td=n*L*Ipk/(Vo+Vf)
    print(f'L={L*1e6:.0f}u Ipk={Ipk:.2f} ton={ton*1e6:.2f}us D={ton/T:.3f} td={td*1e6:.2f} ton+td={(ton+td)*1e6:.2f}')
for V in (Vin_min,Vin_max): print('Dcrit',V,Vor/(V+Vor))
Dmax=0.70
for V,L in ((Vin_min,11e-6),(Vin_max,9e-6)):
    Ipk=V*Dmax*T/L; P=0.5*L*Ipk**2*f; print(f'Dmax: Vin={V} L={L*1e6:.0f}u Ipk={Ipk:.2f}A Pin={P:.2f}W td={n*L*Ipk/(Vo+Vf)*1e6:.2f}us')
Rt=100e3
RDT=(Rt+1250)*(Dmax*(1.3-0.7)+0.7); print('RDT',RDT)
for R in (110e3,113e3): print('D for',R,(R/(Rt+1250)-0.7)/0.6)
CDT=22e-9; print('soft start tau',113e3*CDT)
E_c=0.5*C*Vo**2; print('Cout energy',E_c)
print('CSCP for 0.2s/0.265s', 12.46*0.2, 3.3/12.46)
# divider
R1=3*562e3; R2=10e3; print('Vout',(1+R1/R2)*1.0, 'Idiv',Vo/(R1+R2)*1e6,'uA','Pdiv',Vo**2/(R1+R2)*1e3,'mW')
# plant
def plant(Vin,R):
    D=Vo/(Vin*math.sqrt(R/(2*Lp*f)))
    Gd0=Vo/D; wp=2/(R*C); Gvc0=Gd0/Vm; K=Gvc0*wp
    return D,Gd0,wp/(2*pi),Gvc0,K
Rf=200e3; Cf=15e-9; Kc=Rf/R1; fz=1/(2*pi*Rf*Cf)
print('Kc',Kc,'fz',fz)
loads={'15 mA':Vo/15e-3,'5.5 mA':31160.,'1 mA':Vo/1e-3,'divider only':R1+R2}
import cmath
def T(s,Vin,R):
    D,Gd0,fp,Gvc0,K=plant(Vin,R)
    Gp=Gvc0/(1+s/(2/(R*C)))
    Gc=(1+s*Rf*Cf)/(s*Cf*R1)
    return Gp*Gc
for name,R in loads.items():
    for Vin in (Vin_min,Vin_nom,Vin_max):
        D,Gd0,fp,Gvc0,K=plant(Vin,R)
        # find crossover
        lo,hi=0.01,1e6
        for _ in range(200):
            mid=math.sqrt(lo*hi)
            if abs(T(2j*pi*mid,Vin,R))>1: lo=mid
            else: hi=mid
        fc=mid; ph=math.degrees(cmath.phase(T(2j*pi*fc,Vin,R)))
        pm=180+ph if ph<0 else ph-180
        print(f'{name:12s} Vin={Vin} R={R/1e3:7.1f}k D={D:.3f} Gd0={Gd0:6.0f} fp={fp:6.2f}Hz Gvc0={20*math.log10(Gvc0):5.1f}dB |Gvc(1k)|={abs(Gvc0/(1+2j*pi*1e3/(2/(R*C)))):5.2f} fc={fc:7.1f}Hz PM={pm:5.1f}')
# ripple
print('out ripple 15mA', 15e-3*8.5e-6/C)
print('COMP ripple', Kc*15e-3*8.5e-6/C)
# windup overshoot estimate
print('overshoot from prop path', (2.3-(0.7+0.6*0.7))/Kc)
# PNP stage
print('Ib min',(5-0.7-2)/4.7e3-0.7/10e3)
print('bleed tau', (R1+R2)*C)
