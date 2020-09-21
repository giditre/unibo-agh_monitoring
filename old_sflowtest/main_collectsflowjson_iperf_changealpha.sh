#!/bin/bash

echo

suffix=$1
ratiolist="$2"
duration=$3
alphalist="$4"

echo "Using suffix $suffix and sampling ratios $ratiolist"
echo

for alpha in $alphalist; do

echo -n $alpha > alpha_ewma.dat

echo "Using alpha = $(cat alpha_ewma.dat)"

for ratio in $ratiolist; do
  # format ratio
  ratio=$(printf "%04d" "$ratio")
  echo "Current sampling ratio: $ratio"

  # find line in /etc/hsflowd.conf file
  line=$(cat /etc/hsflowd.conf | grep -n "sampling =")
  #echo $line
  linenumb=$(echo "$line" | grep -o -e "^[0-9]*" | tr -d "\n")
  if ! [[ $linenumb ]]; then
    echo "Sampling ratio line not found in /etc/hsflowd.conf"
    exit 1
  fi
  sed -i "$linenumb"'s/.*/sampling = '"$ratio"'/g' /etc/hsflowd.conf
  cat /etc/hsflowd.conf | grep -n "sampling ="
  service hsflowd restart
  sleep 3

  # if folder does not exist, create it
  [[ ! -d "alphasampratio$ratio" ]] && mkdir alphasampratio$ratio
  ./collectsflowjson_iperf.sh jsFlow.py iperfcmdlines_${suffix}.txt sflow-temp.json alphasampratio$ratio/sflowtest_${suffix}.json $duration
  mv alphasampratio$ratio/sflowtest_${suffix}.json alphasampratio$ratio/sflowtest_${suffix}_alpha${alpha}.json
  echo
  echo "###---###---###"
  echo

done

done
