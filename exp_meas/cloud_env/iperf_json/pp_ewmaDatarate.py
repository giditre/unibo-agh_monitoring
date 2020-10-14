from sys import argv, stderr
from json import load

import numpy as np
import scipy as sp
import scipy.stats

def mean_std_confidence_interval(data, confidence=0.95):
  a = 1.0 * np.array(data)
  n = len(a)
  m, sd, se = np.mean(a), np.std(a), scipy.stats.sem(a)
  h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
  return m, m - h, m + h, sd

json_fname_list = [fname for fname in argv[1:]]

print(json_fname_list)

#src_ip = "172.31.4.156"
#dst_ip = "172.31.2.16"

#src_ip = "172.31.35.53"
#dst_ip = "172.31.38.178"

src_ip = "172.30.100.101"
dst_ip = "172.30.100.102"

datarate_dict = {}

for json_fname in json_fname_list:
  
  # load json
  with open(json_fname) as f:
    j = load(f)
  
  first_t = -1

  for e in j:
    if first_t == -1:
      first_t = e["timestamp"]
    t = e["timestamp"] - first_t
    v = e["rate"]
    if t not in datarate_dict:
      datarate_dict[t] = [v]
    else:
      datarate_dict[t].append(v)

print(datarate_dict)

min_t = min(list(datarate_dict.keys()))
max_t = max(list(datarate_dict.keys()))

mean_datarate_dict = {}

for t in range(min_t, max_t+1):
  if t in datarate_dict:
    mean_datarate_dict[t], _, _, _ = mean_std_confidence_interval(datarate_dict[t])

print(mean_datarate_dict)

for t in mean_datarate_dict:
  print("{:3}{:15.0f}".format(t, mean_datarate_dict[t]))

