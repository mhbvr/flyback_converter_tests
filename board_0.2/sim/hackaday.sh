#!/bin/bash
# Load sweep: board 0.2 as built vs. the "hackaday recipe" (ceramic input caps at the
# transformer, PCB-like primary loop, CSD18543Q3A + 600 V ultrafast diode). Same DA2033 transformer.
cd "$(dirname "$0")"
IMP="cel=120u resr=2m lesl=1n rw=8m lwire=10n"
NEW="FET=csd18543q3a FETINC=CSD18543Q3A.lib DIO=UF600 DINC=diodes_fit.lib"
# board 0.2 as built (4.8 V), higher loads
V0=170 ./runcase.sh a15 "rload=11.3k ton=4.9u" >/dev/null &
V0=170 ./runcase.sh a25 "rload=6.8k ton=6.2u" >/dev/null &
# recipe, 5 V
env $NEW V0=170 ./runcase.sh b05 "vin=5 $IMP rload=31k ton=3.0u" >/dev/null &
env $NEW V0=170 ./runcase.sh b15 "vin=5 $IMP rload=11.3k ton=4.7u" >/dev/null &
env $NEW V0=170 ./runcase.sh b25 "vin=5 $IMP rload=6.8k ton=6.0u" >/dev/null &
# recipe, 9 V and 12 V (as in the hackaday measurements)
env $NEW V0=170 ./runcase.sh b25v9 "vin=9 $IMP rload=6.8k ton=3.35u" >/dev/null &
env $NEW V0=170 ./runcase.sh b25v12 "vin=12 $IMP rload=6.8k ton=2.5u" >/dev/null &
wait
echo ALLDONE
