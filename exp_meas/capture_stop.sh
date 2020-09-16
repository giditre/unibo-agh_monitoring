hflag=0
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

echo

parentdirname=$(basename $(pwd))

campaignindex=$1

campdirname=camp$(printf "%03d" $campaignindex)
echo "Stopping captures of campaign $campdirname"

# check if campaign is already stopped
if grep "STOPPED" $campdirname/capture_status.txt >/dev/null 2>&1; then
  echo "Campaign's status is STOPPED already"
  echo
  exit 0
fi

cat $campdirname/capture_specs.txt | grep -v "^#" | cut -d',' -f1 | sort | uniq | while read remhost; do

  # check if current remhost is actually local host
  if [[ $(hostname | cut -d'.' -f1) == $remhost ]]; then
    # no need to launch remote commands
    echo "Stop local capture on $remhost"
    kill $(cat $campdirname/dumpports.pid)
    rm $campdirname/dumpports.pid
    echo "STOPPPED" > $campdirname/capture_status.txt
    # no need to copy capture files locally

  else
    # launch remote command
    echo "Stop remote capture on $remhost"
    ssh $remhost "cd /root/$parentdirname; kill "'$(cat '"$campdirname"'/dumpports.pid)'"; rm $campdirname/dumpports.pid" < /dev/null
    # copy remote capture files
    scp root@$remhost:/root/$parentdirname/$campdirname/*.dat $campdirname/ < /dev/null
  fi
  echo
done


