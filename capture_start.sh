#!/bin/bash

specsfilename=$1

if ! [[ $specsfilename ]]; then
  echo "Must specify a specifications file name."
  exit 1
fi

echo

parentdirname=$(basename $(pwd))

campaignindex=$(( $(if ls -d */ | grep -e "^camp.*\/" >/dev/null 2>&1; then ls -d camp*/ | sort -r | head -1 | sed 's/^camp0*//g' | sed 's/\/$//g'; fi) + 1 ))
echo "Campaign index: $campaignindex"
echo

campdirname=camp$(printf "%03d" $campaignindex)

if ! [[ -d $campdirname ]] ; then
  mkdir $campdirname
fi
# copy specs file to be used to start and stop capture
cp $specsfilename $campdirname/capture_specs.txt

# create status file
echo RUNNING > $campdirname/capture_status.txt

cat $campdirname/capture_specs.txt | grep -v "^#" | while read line; do 
  echo "Specs: $line"
  remhost=$(echo $line | cut -d',' -f1)
  ovsname=$(echo $line | cut -d',' -f2)
  portnum=$(echo $line | cut -d',' -f3)
  direction=$(echo $line | cut -d',' -f4)

  capfilename=$remhost\_$ovsname\_$portnum\_$direction
  echo "Data file name: $capfilename"

  # check if current remhost is actually local host
  if [[ $(hostname | cut -d'.' -f1) == $remhost ]]; then
    # no need to launch remote commands
    echo "Local capture on $remhost"
    while sleep $(printf "0.%03d" "$(( 1000 - $(date +%N | cut -b1-3 | sed 's/^0*//g') ))"); do
      echo "$(date +%s) $(ovs-ofctl dump-ports $ovsname $portnum | grep "$direction pkts" | awk -F'bytes=' '{ print $2 }' | cut -d',' -f1)" >> $campdirname/$capfilename.dat
    done >/dev/null & echo $! >> $campdirname/dumpports.pid
  else
    # launch remote command
    echo "Remote capture on $remhost"
    ssh $remhost "if ! [[ -d /root/$parentdirname ]]; then mkdir /root/$parentdirname; fi; cd /root/$parentdirname; if ! [[ -d $campdirname ]]; then mkdir $campdirname; fi; while sleep "'$(printf "0.%03d" "$(( 1000 - $(date +%N | cut -b1-3 | sed "s/^0*//g") ))"); do echo "$(date +%s) $(ovs-ofctl dump-ports '"$ovsname $portnum"' | grep "'"$direction"' pkts" | awk -F"bytes=" '"'"'{print $2}'"'"' | cut -d"," -f1)" >> '"$campdirname/$capfilename"'.dat; done >/dev/null & echo $!'" >> $campdirname/dumpports.pid" < /dev/null
  fi
  echo
done

echo "Done launching captures for campaign: $campaignindex"
echo


