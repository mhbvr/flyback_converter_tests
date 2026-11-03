"""Make a TI NexFET PSpice .lib usable in ngspice: inline subcircuit .PARAMs
(ngspice did not resolve them inside these subcircuits) and evaluate {expr} fields.
usage: python3 patch_ti.py <in.lib> <out.lib>"""
import re, sys
s = open(sys.argv[1], encoding='latin1').read()
P = {}
def ev(e):
    return eval(e, {}, {k.lower(): v for k, v in P.items()})
for m in re.finditer(r'(?mi)^[ \t]*\.PARAM\s+(\w+)\s+(\S+)', s):
    k, v = m.group(1).lower(), m.group(2).strip('{}')
    P[k] = ev(v.lower())
s = re.sub(r'(?mi)^[ \t]*\.PARAM.*\n', '', s)
def sub(m):
    e = m.group(1)
    if re.search(r'[vi]\(', e, re.I):
        return m.group(0)          # behavioural source expression, keep
    return '%.6g' % ev(e.lower())
s = re.sub(r'\{([^{}]+)\}', sub, s)
# make the helper capacitance subcircuits unique per part (identical names in every TI lib)
part = re.findall(r'(?mi)^\.SUBCKT\s+(\S+)\s+\S+\s+\S+\s+\S+\s*$', s)[-1].lower()
for c in ('cgs', 'cgd', 'cds'):
    s = re.sub(r'(?mi)^(\.subckt\s+)%s(\s)' % c, r'\g<1>%s_%s\2' % (c, part), s)
    s = re.sub(r'(?mi)^(\.ends\s+)%s\b' % c, r'\g<1>%s_%s' % (c, part), s)
    s = re.sub(r'(?mi)^(x\w+(?:\s+\S+){4}\s+)%s\s*$' % c, r'\g<1>%s_%s' % (c, part), s)
open(sys.argv[2], 'w').write(s)
print('patched', sys.argv[2], 'params:', P)
