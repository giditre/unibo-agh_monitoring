#!/bin/bash

# Define stderr echo function
printf_err() { printf "$@" 1>&2; }

fname=$1

pktcount=0
ethsum=0
ipsum=0
udpsum=0

tshark -r $fname -d udp.port==16343,sflow -Y 'sflow && sflow_245.sampletype==1' -T fields -E separator=' ' -e frame.len -e sflow_245.numsamples 2>/dev/null | python3.6 <(
cat <<-EOF
import sys
import json

accumulator = {}

for line in sys.stdin.readlines():
  line = line.strip('\n').strip()
  if line:
    eth_size, n_samples = line.split()
    if n_samples in accumulator:
      accumulator[n_samples]['data'] += int(eth_size)
      accumulator[n_samples]['count'] += 1
    else:
      accumulator[n_samples] = {
        'data': int(eth_size),
        'count': 1
      }

for n_samples in accumulator:
  accumulator[n_samples]['mean_eth_size'] = int(accumulator[n_samples]['data']/accumulator[n_samples]['count'])
  accumulator[n_samples]['expected_eth_size'] = 14+20+8+28+int(n_samples)*216
  accumulator[n_samples]['avg_additional_overhead'] = accumulator[n_samples]['mean_eth_size']-accumulator[n_samples]['expected_eth_size']
print(json.dumps(accumulator, indent=2, sort_keys=True))



#overhead_accum = 0
#count_accum = 0
#for n_samples in accumulator:
#  overhead_accum += accumulator[n_samples]['avg_additional_overhead']*accumulator[n_samples]['count']
#  count_accum += accumulator[n_samples]['count']
#print('{}'.format(int(overhead_accum/count_accum)))

EOF

)
