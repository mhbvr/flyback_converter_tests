import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def rd(f):
    d={}
    for l in open(f):
        k,_,v=l.rstrip().rpartition(' ')
        try: d[k.strip()]=float(v)
        except: pass
    return d
g=rd('g1.res'); Pmeas=0.949; Pin_meas=4.8*0.274
items=[('10 µF electrolytic ESR (input ripple)',g['10uF ESR I2R']),('Core loss (fitted from ring decay)',g['core-loss resistor']),
 ('Leakage ringing, ceramics, misc.',g['other (leakage damping, ceramics, probes)']),('MOSFET (hard turn-on, conduction)',g['MOSFET (cond+switch+Coss)']),
 ('Bench supply leads',g['lead I2R']),('Perfboard wiring',g['perfboard wiring I2R']),('MCP1407 driver + gate charge',g['driver (MCP1407 + gate charge)']),
 ('Diode QH05TZ600',g['diode']),('Primary DCR',g['primary DCR']),('Secondary DCR',g['secondary DCR']),
 ('Not explained by model (measured − simulated output)',g['Pout (into Cout+R)']-Pmeas)]
fig,ax=plt.subplots(figsize=(10,5.2))
lab=[i[0] for i in items][::-1]; val=[i[1]*1000 for i in items][::-1]
cols=['#9aa5b1' if 'Not explained' in l else '#2a6f97' for l in lab]
b=ax.barh(lab,val,color=cols,height=0.6)
for r,v in zip(b,val): ax.text(v+2,r.get_y()+r.get_height()/2,f'{v:.0f} mW ({v/1000/Pin_meas*100:.1f} %)',va='center',fontsize=9,color='#333')
ax.set_xlabel('loss [mW]  (percent of measured Pin = 1.315 W)'); ax.set_xlim(0,max(val)*1.35)
ax.spines[['top','right']].set_visible(False); ax.grid(axis='x',color='#e5e5e5'); ax.set_axisbelow(True)
ax.set_title('Board 0.2 loss budget: fitted ngspice model vs. measurement (Pout meas = 0.949 W)',fontsize=11,loc='left')
plt.tight_layout(); plt.savefig('loss_budget.png',dpi=100)
cases=[('Measured board 0.2',0.7215),('Sim: datasheet-nominal parasitics',rd('b0.res')['eff']),('Sim: fitted to measurement',rd('g1.res')['eff']),
 ('Sim: fitted + valley turn-on (109 kHz)',rd('w2.res')['eff']),('Sim: fitted + low-ESR input cap',rd('w1.res')['eff']),('Sim: fitted + both',rd('w3.res')['eff'])]
fig,ax=plt.subplots(figsize=(10,3.6)); lab=[c[0] for c in cases][::-1]; val=[c[1]*100 for c in cases][::-1]
b=ax.barh(lab,val,color=['#2a6f97']*5+['#333333'],height=0.6)
for r,v in zip(b,val): ax.text(v+0.4,r.get_y()+r.get_height()/2,f'{v:.1f} %',va='center',fontsize=9)
ax.set_xlim(60,95); ax.set_xlabel('efficiency Pout/Pin [%]'); ax.spines[['top','right']].set_visible(False); ax.grid(axis='x',color='#e5e5e5'); ax.set_axisbelow(True)
plt.tight_layout(); plt.savefig('whatif.png',dpi=100)
