#!/bin/bash
# Reproduce all cases of ANALYSIS.md (needs ngspice >= 40, python3 + numpy/scipy/matplotlib)
set -e; cd "$(dirname "$0")"
[ -f CSD18533KCS.lib ] || ./get_models.sh
V0=183 ./runcase.sh b0 "Lp=10u resr=0.30 csec=60p" >/dev/null &   # datasheet-nominal
V0=180 ./runcase.sh g1 "" >/dev/null &                              # fitted (netlist defaults)
V0=195 ./runcase.sh w1 "resr=0.02" >/dev/null &                     # low-ESR input capacitor
V0=180 ./runcase.sh w2 "fsw=108.93k ton=3.26u" >/dev/null &         # valley turn-on
V0=190 ./runcase.sh w3 "resr=0.02 fsw=108.93k ton=3.26u" >/dev/null & # both
wait
for n in b0 g1 w1 w2 w3; do echo "== $n"; cat $n.res; done
python3 overlay.py g1.dat.npy img/ov_g1.png
python3 bars.py && mv loss_budget.png whatif.png img/
