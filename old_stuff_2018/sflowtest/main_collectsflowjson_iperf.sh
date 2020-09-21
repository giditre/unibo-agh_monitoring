#!/bin/bash

echo

collector=$1
suffix=$2
ratiolist="$3"
duration=$4

echo "Using suffix $suffix and sampling ratios $ratiolist"
echo

for ratio in $ratiolist; do
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

  # format ratio
  ratio=$(printf "%04d" "$ratio")
  echo "Current sampling ratio: $ratio"

  # if folder does not exist, create it
  [[ ! -d "sampratio$ratio" ]] && mkdir sampratio$ratio
  ./collectsflowjson_iperf.sh $collector iperfcmdlines_${suffix}.txt sflow-temp.json sampratio$ratio/sflowtest_${suffix}.json $duration
  echo
  echo "###---###---###"
  echo

done

