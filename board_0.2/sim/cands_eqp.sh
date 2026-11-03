#!/bin/bash
# same candidates, on-time scaled so Pout ~ 1.05 W (as the fitted board-0.2 model)
cd "$(dirname "$0")"
FET=CSD18534KCS FETINC=CSD18534KCS.lib V0=181 ./runcase.sh e_m34 "ton=3.60u" >/dev/null &
FET=csd18543q3a FETINC=CSD18543Q3A.lib V0=181 ./runcase.sh e_m43 "ton=3.58u" >/dev/null &
DIO=UF600 DINC=diodes_fit.lib V0=181 ./runcase.sh e_duf "ton=3.51u" >/dev/null &
FET=CSD18534KCS FETINC=CSD18534KCS.lib DIO=UF600 DINC=diodes_fit.lib V0=181 ./runcase.sh e_c34uf "ton=3.64u" >/dev/null &
FET=csd18543q3a FETINC=CSD18543Q3A.lib DIO=UF600 DINC=diodes_fit.lib V0=181 ./runcase.sh e_c43uf "ton=3.64u" >/dev/null &
wait
echo ALLDONE
