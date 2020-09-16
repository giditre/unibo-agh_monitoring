#!/bin/bash

# flushflag=0
# while getopts 'f' OPTION ; do
#   case $OPTION in
#     f) flushflag=1
#     ;;
#     ?) echo "Unknown parameter $OPTION"
#        exit 1
#     ;;
#   esac
# done
# shift $(($OPTIND-1))

parentdirname=$(basename $(pwd))

echo

hostlist="$(hostname)"

for remhost in $hostlist; do

  # check if current remhost is actually local host
  if [[ $(hostname | cut -d'.' -f1) == $remhost ]]; then
    # no need to launch remote commands
    echo "Kill all processes from script capture_start on $remhost"
    ps --no-headers -Alfww | grep "[c]apture_start" | while read line; do
      pid=$(echo $line | cut -d' ' -f4)
      kill $pid
    done
    rm -r camp*

  else
    # launch remote command
    echo "Kill all processes from scripts in $parentdirname on $remhost"
    ssh $remhost "cd /root/$parentdirname; ps --no-headers -Alfww | grep $parentdirname | while read line; do pid="'$(echo $line | cut -d'"' '"' -f4); kill $pid; done; rm -r camp*' < /dev/null
  fi
  echo
done


