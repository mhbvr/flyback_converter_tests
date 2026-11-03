#!/bin/bash
# Downloads the vendor PSpice model of the CSD18533KCS from ti.com (SLPM047)
# and patches it so it runs in ngspice (PSpice compatibility mode, see .spiceinit).
#  - subcircuit-local .PARAMs are inlined (ngspice did not resolve them)
#  - LEVEL=7 (PSpice BSIM3) is understood by ngspice in "ps" compat mode
set -e
cd "$(dirname "$0")"
tmp=$(mktemp -d)
curl -sSL https://www.ti.com/lit/zip/SLPM047 -o "$tmp/SLPM047.zip"
unzip -o -q "$tmp/SLPM047.zip" -d "$tmp"
python3 - "$tmp/CSD18533KCS.lib" CSD18533KCS.lib <<'PY'
import re, sys
s = open(sys.argv[1], encoding='latin1').read()
for k, v in {'{pwidthP}': '4.02', '{perimP}': '8.442', '{ptrc1}': '7.00e-3', '{ptrc2}': '2.0e-5'}.items():
    s = s.replace(k, v)
s = re.sub(r'(?m)^[ \t]*\.PARAM.*\n', '', s)
s = s.replace('DBD {4.02/5.788666666666666666666666666666666666666666666667}', 'DBD 0.69446')
s = s.replace('{0.45e-3+1.3e-3*0}', '0.45e-3').replace('{0.5e-4+1.42e-3}', '1.47e-3')
open(sys.argv[2], 'w').write(s)
PY
rm -rf "$tmp"
echo "CSD18533KCS.lib ready"
