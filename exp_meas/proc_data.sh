#!/bin/bash

infname=$1

if ! [[ $infname ]] ; then
  echo "Must provide an input file name."
  exit 1
fi

if [[ $2 ]] ; then
  outfname=$2
else
  outfname=procd_$infname
fi

inittime=$(head -1 $infname | cut -d' ' -f1)
prevvalue=$(head -1 $infname | cut -d' ' -f2)

cat $infname | tail -n +1 | while read line; do
  currtime=$(echo $line | cut -d' ' -f1)
  currvalue=$(echo $line | cut -d' ' -f2)
  printf "%3d %15d\n" "$(( $currtime - $inittime ))" "$(( $currvalue - $prevvalue ))" | tee -a $outfname
  prevvalue=$currvalue
done

