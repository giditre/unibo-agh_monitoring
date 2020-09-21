#!/bin/bash

# Define stderr echo function
printf_err() { printf "$@" 1>&2; }

fname=$1

sampratio=$2

numsamples=$3

tshark -r $fname -d udp.port==16343,sflow -Y "sflow && sflow_245.sampletype==1 && sflow_245.numsamples==$numsamples" -T fields -E separator=' ' -e frame.len -e sflow_245.numsamples -e ip.len -e sflow_5.sample_length -e sflow_245.sequence_number -e sflow_245.sampletype 2>/dev/null | python3.6 <(
cat <<-EOF
import sys
import json

relative_overhead_list = []

for line in sys.stdin.readlines():
  line = line.strip('\n').strip()
  print(line)

  if line:
    splitted_line = line.split()

    sflow_eth_len = int(splitted_line[0])
    n_samples = int(splitted_line[1])
    sampled_packets_ip_len_list = [ int(n) for n in splitted_line[2].split(',') ]
    sflow_sample_len_list = [ int(n)+8 for n in splitted_line[3].split(',') ]
    sflow_sample_type_list = [ int(n) for n in splitted_line[5].split(',') ]

    if n_samples != len(sampled_packets_ip_len_list)-1:
      print(line + ' mismatch with number of IP headers')
      continue
    if n_samples != len(sflow_sample_len_list):
      print(line + ' mismatch with number of sFlow sample headers')
      continue

    n_counter_samples = 0
    n_valid_samples = 0
    sampled_packets_eth_len = 0
    ip_len_index = 1

    for i in range(n_samples):
      if sflow_sample_type_list[i] == 1:
        if sampled_packets_ip_len_list[ip_len_index] >= sflow_sample_len_list[i]:
          n_valid_samples += 1
          
          # calcolare per ogni linea il rapporto tra la dimensione del pacchetto sFlow più esterno
          # e la quantità di traffico utile che questo pacchetto campiona + la dimensione del pacchetto sFlow stesso e verificare se è vicina a 1.8%
          # la quantità di traffico utile che il pacchetto campiona è la somma di tutte le ip_len+14 che si vedono in quella riga per pacchetti validi, per N

          sampled_packets_eth_len += sampled_packets_ip_len_list[ip_len_index] + 14
          ip_len_index += 1
      else:
        n_counter_samples += 1

    if n_valid_samples > 0:
      relative_overhead = ( sflow_eth_len / ( sflow_eth_len + sampled_packets_eth_len * $sampratio ) ) * 100

      relative_overhead_list.append(relative_overhead)

      print('{} {:.2f}%'.format(line, relative_overhead))

if relative_overhead_list:
  print('Average relative overhead: {:.5f}'.format(sum(relative_overhead_list)/len(relative_overhead_list)))

EOF
)
