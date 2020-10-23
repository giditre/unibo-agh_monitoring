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

src_ip = "172.30.100.101"
dst_ip = "172.30.100.102"

datarate_dict = {}

monitoring_fname = argv[1]
  
# load monitoring json
with open(monitoring_fname) as f:
  monit_j = load(f)

iperf_fname = monitoring_fname.replace("monitoring", "iperf")

# load iperf json
with open(iperf_fname) as f:
  iperf_j = load(f)

for e in monit_j:
  for f in e['flows']:
    # check if flow is between desired src and dst
    #if f["srcIP"] == src_ip and f["dstIP"] == dst_ip:
    #if f["inputPort"] == 2 and f["srcIP"] == src_ip and f["dstIP"] == dst_ip:
    if f["inputPort"] == 1073741823 and f["srcIP"] == src_ip and f["dstIP"] == dst_ip:
      t = e["timestamp"]
      v = f["ewmaDatarate"]
      datarate_dict[t] = {
        "monit": v,
        "iperf": 0
      }

#print(datarate_dict)

for e in iperf_j:
  t = e["timestamp"]
  v = e["rate"]
  if t in datarate_dict:
    datarate_dict[t]["iperf"] = v

first_t = min(list(datarate_dict.keys()))

print("{:6}{:15}{:15}".format("Time", "iperf", "sflow"))
for t in datarate_dict:
  print("{:6}{:15.0f}{:15.0f}".format(t-first_t, datarate_dict[t]["iperf"], datarate_dict[t]["monit"]))

