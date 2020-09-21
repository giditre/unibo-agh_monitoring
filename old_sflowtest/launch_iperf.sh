#!/bin/bash

iperfcmdfname=$1
if ! [[ -f $iperfcmdfname ]]; then
  echo "Error: file $iperfcmdfname not found."
  exit 1
fi
shift

# load iperf commands from file
declare -a iperfcmd
while read time ser cli; do
  echo "At t=$time will launch iperf server with $ser and iperf client with $cli"
  iperfcmd[$time]="$ser;$cli"
done < $iperfcmdfname
echo

TIMEOUT=$1

starttime=$(date +%s)

while sleep $(printf "0.%03d" "$(( 1000 - $(date +%N | cut -b1-3 | sed 's/^0*//g') ))"); do
  currtime=$(( $(date +%s) - $starttime ))

  echo "$currtime/$TIMEOUT ( $(( $currtime * 100 / $TIMEOUT ))% )"

  # check if it's time to launch iperf
  if [[ "${iperfcmd[$currtime]}" ]]; then
    # retrieve HTTP requests
    iperfcmdser=$(echo ${iperfcmd[$currtime]} | cut -d';' -f1)
    iperfcmdcli=$(echo ${iperfcmd[$currtime]} | cut -d';' -f2)
    # launch iperf
    serfname=$(curl -X GET $iperfcmdser 2>/dev/null)
    clifname=$(curl -X GET $iperfcmdcli 2>/dev/null)
    iperfcmd[$currtime]="${iperfcmd[$currtime]};$serfname;$clifname"
    echo "Started iperf: ${iperfcmd[$currtime]}"
  fi

  if [[ $(( $(date +%s) - $starttime )) -gt $TIMEOUT ]]; then
    echo "Reached timeout."
    echo
    break
  else
    if [ "$validjson" = true ]; then
      echo "," >> $dstfile
    fi
  fi

done

