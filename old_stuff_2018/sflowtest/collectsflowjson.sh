#!/bin/bash

srcfile=$1
dstfile=$2

TIMEOUT=$3

if ! [[ -f $srcfile ]]; then
  echo "Error: source file does not exist"
  exit 1
fi

if [[ -f $dstfile ]]; then
  echo "Destination file already exists. Overwrite it? [y/n]"
  read response
  if [[ $response != y ]]; then
    echo "Interrupted."
    exit 2
  fi
fi

# start packet capture
capfname=$(echo "$dstfile" | rev | cut -d. -f2- | rev).cap
tcpdump -i lo -w $capfname udp and port 16343 >/dev/null 2>&1 & echo -n "$!" > tcpdump.pid

echo "[" > $dstfile

starttime=$(date +%s)

while sleep $(printf "0.%03d" "$(( 1000 - $(date +%N | cut -b1-3 | sed 's/^0*//g') ))"); do
  currjson=$(cat $srcfile)
  if [[ $currjson ]]; then
    echo $currjson | tee -a $dstfile
  fi
  
  if [[ $(( $(date +%s) - $starttime )) -gt $TIMEOUT ]]; then
    echo "Reached timeout."
    break
  else
    echo "," >> $dstfile
  fi
done

echo "]" >> $dstfile

kill $(cat tcpdump.pid)
rm tcpdump.pid

