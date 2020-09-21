#!/bin/bash

# Define stderr echo function
printf_err() { printf "$@" 1>&2; }

fname=$1

pktcount=0
ethsum=0
ipsum=0
udpsum=0

tshark -r $fname -d udp.port==16343,sflow -T fields -E separator=' ' -e frame.len 2>/dev/null | while true; do
  if read line; then
    ethsize=$(echo $line | cut -d' ' -f1)
    ethsum=$(( $ethsum + $ethsize ))
    #ipsize=$(echo $line | cut -d' ' -f2 | cut -d',' -f1)
    #ipsum=$(( $ipsum + $ipsize ))
    #udpsize=$(echo $line | cut -d' ' -f3 | cut -d',' -f1)
    #udpsum=$(( $udpsum + $udpsize ))
    count=$(( $count + 1 ))
    printf_err "\r# %d" $count
  else
    printf_err "\n"
    echo "N $count eth $ethsum"
    break
  fi
done

