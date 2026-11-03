#!/bin/bash
cd "$(dirname "$0")"
FET=CSD18534KCS FETINC=CSD18534KCS.lib V0=181 ./runcase.sh m34 "" >/dev/null &
FET=csd18543q3a FETINC=CSD18543Q3A.lib V0=181 ./runcase.sh m43 "" >/dev/null &
DIO=byg20j DINC=byg20j.lib V0=180 ./runcase.sh d20 "" >/dev/null &
DIO=UF600 DINC=diodes_fit.lib V0=181 ./runcase.sh duf "" >/dev/null &
V0=180 ./runcase.sh g1 "" >/dev/null &
wait
FET=csd18543q3a FETINC=CSD18543Q3A.lib DIO=UF600 DINC=diodes_fit.lib V0=182 ./runcase.sh c43uf "" >/dev/null &
FET=CSD18534KCS FETINC=CSD18534KCS.lib DIO=UF600 DINC=diodes_fit.lib V0=182 ./runcase.sh c34uf "" >/dev/null &
FET=csd18543q3a FETINC=CSD18543Q3A.lib DIO=UF600 DINC=diodes_fit.lib V0=192 ./runcase.sh c43uf_lowesr_valley "resr=0.02 fsw=108.93k ton=3.26u" >/dev/null &
wait
echo ALLDONE
