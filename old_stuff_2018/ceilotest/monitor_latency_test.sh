#!/bin/bash

period=$1

c=1

while sleep $(printf "0.%03d" "$(( 1000 - $(date +%N | cut -b1-3 | sed 's/^0*//g') ))"); do
  if [[ $c == $period ]] ; then
    date
    #/usr/bin/python3.6 gnocchi_get.py -m gnocchi_metrics.json -l 1 "metric"
    /usr/bin/python3.6 gnocchi_get.py -l 1 "metric/1d9fa69a-d1de-442d-9f09-4a87589e6cf3/measures" 2>/dev/null
    echo
    c=0
  fi
  c=$(( $c + 1 ))
done

