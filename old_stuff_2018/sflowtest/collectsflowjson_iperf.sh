#!/bin/bash

echo

sflowcollectorfname=$1
if ! [[ -f $sflowcollectorfname ]]; then
  echo "Error: file $sflowcollectorfname not found."
  exit 1
fi
shift

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

##for key in "${!iperfcmd[@]}"; do printf "%s %s\n" "$key" "${iperfcmd[$key]}"; done
#for key in $(seq 30); do
#  if [[ "${iperfcmd[$key]}" ]]; then
#    echo "At $key seconds do ${iperfcmd[$key]}"
#  else
#    echo "At $key seconds do nothing."
#  fi
#done
#exit 1

srcfile=$1
dstfile=$2

TIMEOUT=$3

if ! [[ -f $srcfile ]]; then
  echo "Error: source file does not exist"
  exit 1
fi

#if [[ -f $dstfile ]]; then
#  echo "Destination file already exists. Overwrite it? [y/n]"
#  read response
#  if [[ $response != y ]]; then
#    echo "Interrupted."
#    exit 1
#  fi
#  echo
#fi

# start sFlow collector
echo "Starting sFlow collector..."
python $sflowcollectorfname > sflowcollector.log 2>&1 & echo -n "$!" > sflowcollector.pid
sleep 3
echo "Done."
echo

# start packet capture
capfname=$(echo "$dstfile" | rev | cut -d. -f2- | rev).cap
tcpdump -i lo -w $capfname udp and port 16343 >/dev/null 2>&1 & echo -n "$!" > tcpdump.pid
echo "Started packet capture to $capfname"
echo

# initialize json file
echo "[" > $dstfile

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

  # check if valid JSON
  validjson=false
  if [[ $(cat $srcfile) ]] && python -m json.tool "$srcfile" > /dev/null 2>&1; then
    cat $srcfile >> $dstfile
    validjson=true
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

# close json file
echo "]" >> $dstfile

# stop packet capture
echo "Stopping packet capture"
kill $(cat tcpdump.pid)
rm tcpdump.pid

# stop sFlow collector
echo "Stopping sFlow collector"
kill -INT $(cat sflowcollector.pid)
rm sflowcollector.pid
sleep 3
mv sflow_allDataPerSecond.json $(echo $dstfile | sed 's/\.json$/_allDataPerSecond.json/g')

# # retrieve iperf logs
# for t in "${!iperfcmd[@]}"; do
#   # retrieve HTTP requests and file names
#   iperfcmdser=$(echo ${iperfcmd[$t]} | cut -d';' -f1 | awk -F '/iperf' '{print $1}')
#   iperfcmdcli=$(echo ${iperfcmd[$t]} | cut -d';' -f2 | awk -F '/iperf' '{print $1}')
#   serfname=$(echo ${iperfcmd[$t]} | cut -d';' -f3)
#   clifname=$(echo ${iperfcmd[$t]} | cut -d';' -f4)
# 
#   # retreve logs from HTTP endpoints
# 
#   serlogfname=$(echo "$dstfile" | rev | cut -d. -f2- | rev)_${t}_iperfser.log
#   # remove previous log for same test, if any
#   [[ -f $serlogfname ]] && rm $serlogfname
#   while ! [[ -s $serlogfname ]]; do
#     curl -X GET "$iperfcmdser/$serfname" > $serlogfname 2>/dev/null
#     if ! [[ -s $serlogfname ]]; then
#       echo "Waiting for iperf server output to become available..."
#       sleep 3
#     fi
#   done    
#   echo
#   
#   cat $serlogfname
#   echo
# 
#   clilogfname=$(echo "$dstfile" | rev | cut -d. -f2- | rev)_${t}_iperfcli.log
#   [[ -f $clilogfname ]] && rm $clilogfname
#   curl -X GET "$iperfcmdcli/$clifname" > $clilogfname 2>/dev/null
#   cat $clilogfname
#   echo
# 
# done

