#!/bin/bash
# Cheaper-MOSFET sensitivity: generic switch (genfet.lib) swept in Ron / gate charge / Coss,
# plus TI's real CSD18541F5 model. Diode stays QH05TZ600 to isolate the MOSFET effect.
cd "$(dirname "$0")"
F=genfet.lib
FET="GENFET ron=6.5m cg=3n coss=800p" FETINC=$F V0=180 ./runcase.sh gcal "" >/dev/null &   # CSD18533-like (calibration)
FET="GENFET ron=15m cg=2n coss=300p"  FETINC=$F V0=180 ./runcase.sh gA "" >/dev/null &     # 15 mohm, 10 nC
FET="GENFET ron=35m cg=9.6n coss=400p" FETINC=$F V0=180 ./runcase.sh gC "" >/dev/null &    # IRLZ44N-like (48 nC)
FET="GENFET ron=50m cg=3n coss=250p"  FETINC=$F V0=180 ./runcase.sh gB "" >/dev/null &     # FQP30N06L-like
FET="GENFET ron=100m cg=0.6n coss=60p" FETINC=$F V0=180 ./runcase.sh gD "" >/dev/null &    # small SOT-23 60 V
FET="GENFET ron=200m cg=0.4n coss=40p" FETINC=$F V0=180 ./runcase.sh gE "" >/dev/null &    # tiny 60 V
FET=CSD18541F5 FETINC=CSD18541F5.lib V0=180 ./runcase.sh f41 "" >/dev/null &              # TI femtoFET, real model
wait
echo ALLDONE
