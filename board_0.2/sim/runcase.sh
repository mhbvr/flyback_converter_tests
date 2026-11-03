#!/bin/bash
name=$1; shift; ov="$*"; v=${V0:-172}
for it in 1 2 3; do
  cp flyback.cir ${name}_run.cir
  sed -i -e "s/^\.param vtop=.*/.param vtop=$v/" -e "s/out\.dat/$name.dat/" ${name}_run.cir
  for kv in $ov; do k=${kv%%=*}; val=${kv#*=}; sed -i -E "/^\.param/ s/(\s)$k=[^ ]+/\1$k=$val/" ${name}_run.cir; done
  ngspice -b ${name}_run.cir > $name.log 2>&1
  args=$(echo $ov | tr ' ' '\n' | grep -E '^(resr|rlead|rcore)=' | tr '\n' ' ')
  python3 post.py $name.dat $args > $name.res
  vn=$(grep 'Vout steady' $name.res | awk '{print $NF}')
  v=$(python3 -c "print(round(0.4*$v+0.6*$vn,1))")
done
echo "== $name ($ov) final IC=$v"; cat $name.res
